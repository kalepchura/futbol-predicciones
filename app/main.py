from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime
from jose import jwt
from passlib.context import CryptContext
import random, string, os

from app.database import engine, get_db, Base
from app import models, schemas
from app.scoring import calcular_puntos, calcular_bonus_racha

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Futbol Predicciones")

# Montar estáticos (frontend)
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

SECRET_KEY = "clave_secreta_lab"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generar_token(nombre: str):
    return jwt.encode({"sub": nombre}, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Token inválido")

def get_usuario_actual(token: str, db: Session):
    nombre = verificar_token(token)
    usuario = db.query(models.Usuario).filter(models.Usuario.nombre == nombre).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario

def codigo_aleatorio():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ── AUTH ──────────────────────────────────────────────
@app.post("/registro", response_model=schemas.Token)
def registro(data: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(models.Usuario).filter(models.Usuario.nombre == data.nombre).first():
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    usuario = models.Usuario(
        nombre=data.nombre,
        password=pwd_context.hash(data.password)
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return {"access_token": generar_token(usuario.nombre), "token_type": "bearer"}

@app.post("/login", response_model=schemas.Token)
def login(data: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.nombre == data.nombre).first()
    if not usuario or not pwd_context.verify(data.password, usuario.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"access_token": generar_token(usuario.nombre), "token_type": "bearer"}

# ── SALAS ─────────────────────────────────────────────
@app.post("/salas")
def crear_sala(data: schemas.SalaCreate, token: str, db: Session = Depends(get_db)):
    usuario = get_usuario_actual(token, db)
    sala = models.Sala(
        nombre=data.nombre,
        codigo=codigo_aleatorio(),
        creador_id=usuario.id
    )
    db.add(sala)
    db.commit()
    db.refresh(sala)
    miembro = models.SalaUsuario(sala_id=sala.id, usuario_id=usuario.id)
    db.add(miembro)
    db.commit()
    return {"sala_id": sala.id, "codigo": sala.codigo, "nombre": sala.nombre}

@app.post("/salas/unirse")
def unirse_sala(data: schemas.SalaUnirse, token: str, db: Session = Depends(get_db)):
    usuario = get_usuario_actual(token, db)
    sala = db.query(models.Sala).filter(models.Sala.codigo == data.codigo).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    ya_miembro = db.query(models.SalaUsuario).filter_by(sala_id=sala.id, usuario_id=usuario.id).first()
    if ya_miembro:
        raise HTTPException(status_code=400, detail="Ya eres miembro")
    db.add(models.SalaUsuario(sala_id=sala.id, usuario_id=usuario.id))
    db.commit()
    return {"mensaje": f"Te uniste a la sala {sala.nombre}"}

@app.get("/salas/{sala_id}/ranking")
def ranking(sala_id: int, db: Session = Depends(get_db)):
    sala = db.query(models.Sala).filter_by(id=sala_id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    miembros = db.query(models.SalaUsuario).filter_by(sala_id=sala_id).all()
    resultado = [{"usuario": m.usuario.nombre, "puntos": m.puntos_total} for m in miembros]
    return sorted(resultado, key=lambda x: x["puntos"], reverse=True)

@app.get("/salas/{sala_id}/partidos")
def listar_partidos(sala_id: int, db: Session = Depends(get_db)):
    sala = db.query(models.Sala).filter_by(id=sala_id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    partidos = db.query(models.Partido).filter_by(sala_id=sala_id).all()
    return [
        {
            "id": p.id,
            "equipo_local": p.equipo_local,
            "equipo_visitante": p.equipo_visitante,
            "fecha_partido": p.fecha_partido,
            "goles_local": p.goles_local,
            "goles_visitante": p.goles_visitante,
            "finalizado": p.finalizado,
        }
        for p in partidos
    ]

# ── PARTIDOS ──────────────────────────────────────────
@app.post("/salas/{sala_id}/partidos")
def crear_partido(sala_id: int, data: schemas.PartidoCreate, token: str, db: Session = Depends(get_db)):
    usuario = get_usuario_actual(token, db)
    sala = db.query(models.Sala).filter_by(id=sala_id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    if sala.creador_id != usuario.id:
        raise HTTPException(status_code=403, detail="Solo el creador puede agregar partidos")
    partido = models.Partido(
        sala_id=sala_id,
        equipo_local=data.equipo_local,
        equipo_visitante=data.equipo_visitante,
        fecha_partido=data.fecha_partido
    )
    db.add(partido)
    db.commit()
    db.refresh(partido)
    return {"partido_id": partido.id}

@app.post("/partidos/{partido_id}/resultado")
def registrar_resultado(partido_id: int, data: schemas.ResultadoCreate, token: str, db: Session = Depends(get_db)):
    usuario = get_usuario_actual(token, db)
    partido = db.query(models.Partido).filter_by(id=partido_id).first()
    if not partido:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    # Solo el creador de la sala puede registrar resultado
    sala = db.query(models.Sala).filter_by(id=partido.sala_id).first()
    if sala.creador_id != usuario.id:
        raise HTTPException(status_code=403, detail="Solo el creador puede registrar resultados")

    partido.goles_local = data.goles_local
    partido.goles_visitante = data.goles_visitante
    partido.finalizado = True

    # Calcular puntos base para cada predicción (R1, R2, R3, R5)
    predicciones = db.query(models.Prediccion).filter_by(partido_id=partido_id).all()
    for pred in predicciones:
        pred.puntos = calcular_puntos(
            pred.goles_local, pred.goles_visitante,
            data.goles_local, data.goles_visitante,
            pred.fecha_prediccion, partido.fecha_partido
        )
    db.commit()

    # Recalcular puntos totales de cada usuario en la sala (incluyendo bonus racha R4)
    usuarios_en_partido = {p.usuario_id for p in predicciones}
    for usuario_id in usuarios_en_partido:
        todas = (
            db.query(models.Prediccion)
            .join(models.Partido)
            .filter(
                models.Partido.sala_id == partido.sala_id,
                models.Prediccion.usuario_id == usuario_id,
                models.Partido.finalizado == True
            )
            .order_by(models.Partido.fecha_partido)
            .all()
        )
        historial = [
            (p.goles_local, p.goles_visitante, p.partido.goles_local, p.partido.goles_visitante)
            for p in todas
        ]
        bonus = calcular_bonus_racha(historial)
        puntos_base = sum(p.puntos for p in todas)

        sala_usuario = db.query(models.SalaUsuario).filter_by(
            sala_id=partido.sala_id, usuario_id=usuario_id
        ).first()
        if sala_usuario:
            sala_usuario.puntos_total = puntos_base + bonus

    db.commit()
    return {"mensaje": "Resultado registrado y puntos calculados"}

# ── PREDICCIONES ──────────────────────────────────────
@app.post("/partidos/{partido_id}/predicciones")
def hacer_prediccion(partido_id: int, data: schemas.PrediccionCreate, token: str, db: Session = Depends(get_db)):
    usuario = get_usuario_actual(token, db)
    partido = db.query(models.Partido).filter_by(id=partido_id).first()
    if not partido:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    if partido.finalizado:
        raise HTTPException(status_code=400, detail="Partido ya finalizado")
    ya = db.query(models.Prediccion).filter_by(usuario_id=usuario.id, partido_id=partido_id).first()
    if ya:
        raise HTTPException(status_code=400, detail="Ya predijiste este partido")
    pred = models.Prediccion(
        usuario_id=usuario.id,
        partido_id=partido_id,
        goles_local=data.goles_local,
        goles_visitante=data.goles_visitante
    )
    db.add(pred)
    db.commit()
    return {"mensaje": "Predicción registrada"}