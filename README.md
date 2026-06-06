# ⚽ futbol-predicciones

Aplicación web para predecir resultados del Mundial de fútbol. Los usuarios se organizan en salas privadas, registran sus predicciones y acumulan puntos automáticamente según 5 reglas de puntuación.

Proyecto universitario — Desarrollo de Soluciones en la Nube · 5 C24

---

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | Python 3.11 + FastAPI |
| Base de datos | PostgreSQL 15 |
| Frontend | HTML + CSS + JavaScript Vanilla |
| Infraestructura | Docker + Docker Compose |
| Load Balancer | Nginx (3 instancias en round-robin) |
| Tests de carga | Locust |

---

## Levantar el proyecto

### Requisitos
- Docker
- Docker Compose

### Comandos

```bash
# Clonar el repositorio
git clone https://github.com/kalepchura/futbol-predicciones.git
cd futbol-predicciones

# Levantar todos los servicios
docker-compose up --build

# La aplicación queda disponible en:
# http://localhost
```

### Servicios que se levantan

| Servicio | Descripción | Puerto interno |
|----------|-------------|----------------|
| `db` | PostgreSQL 15 | 5432 |
| `app1` / `app2` / `app3` | FastAPI (3 instancias) | 8000 |
| `nginx` | Load balancer | 80 (expuesto) |

---

## Estructura del proyecto

```
futbol-predicciones/
├── app/
│   ├── main.py           # Todos los endpoints REST
│   ├── models.py         # Modelos SQLAlchemy
│   ├── database.py       # Conexión PostgreSQL
│   ├── schemas.py        # Validación Pydantic
│   ├── scoring.py        # Sistema de puntuación (5 reglas)
│   └── static/
│       ├── index.html    # Login / Registro
│       ├── salas.html    # Gestión de salas
│       ├── partidos.html # Predicciones de partidos
│       └── ranking.html  # Tabla de puntuaciones
├── nginx/
│   └── nginx.conf        # Configuración del load balancer
├── tests/
│   └── locustfile.py     # Stress testing
├── ARCHITECTURE.md       # Plano técnico del sistema
├── CONVENTIONS.md        # Reglas de código para el equipo
├── CLAUDE.md             # Contexto para Claude Code
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Sistema de puntuación

| Regla | Condición | Puntos |
|-------|-----------|--------|
| R1 — Resultado exacto | Marcador exacto correcto | +5 |
| R2 — Ganador correcto | Equipo ganador o empate correcto | +3 |
| R3 — Diferencia de goles | Margen de victoria correcto | +2 |
| R4 — Bonus por racha | Cada 3 partidos consecutivos acertados | +2 extra |
| R5 — Predicción anticipada | Predicción registrada >24h antes | +1 extra |

---

## Flujo de trabajo (Git)

```
feature/frontend  ──┐
                    ├──► dev ──► main
feature/backend   ──┘
```

- Nunca se hace push directo a `main`
- Todo cambio pasa por Pull Request
- `main` = código de entrega final

---

## Equipo

| Rol | Responsabilidad |
|-----|-----------------|
| Backend | FastAPI, PostgreSQL, scoring, Docker, Nginx, stress testing |
| Frontend | HTML/JS, integración API, documentación, arquitectura |

---

## Documentación de la API

Con el proyecto corriendo, disponible en:

```
http://localhost/docs
```
