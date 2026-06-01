# CONVENTIONS.md

> Reglas obligatorias para cualquier código generado en este repositorio.

---

# Objetivo

Mantener consistencia entre contribuciones humanas y código generado por IA (Claude Code, ChatGPT, Copilot, etc.).

Antes de modificar cualquier archivo, leer:

1. ARCHITECTURE.md
2. CONVENTIONS.md

---

# Idioma del proyecto

## Código

Todo el código debe escribirse en inglés.

Ejemplos:

Correcto:

```python
user
match
prediction
score
```

Incorrecto:

```python
usuario
partido
prediccion
puntaje
```

---

## Mensajes para el usuario

Los mensajes mostrados al usuario deben estar en español.

Ejemplos:

```python
raise HTTPException(
    status_code=404,
    detail="Sala no encontrada"
)
```

```python
return {
    "mensaje": "Predicción registrada"
}
```

---

# Convenciones de nombres

## Clases

Usar PascalCase.

Ejemplos:

```python
Usuario
Sala
Partido
Prediccion
```

---

## Funciones

Usar snake_case.

Ejemplos:

```python
crear_sala()
hacer_prediccion()
registrar_resultado()
```

---

## Variables

Usar snake_case.

Ejemplos:

```python
usuario_actual
fecha_partido
puntos_total
```

---

## Constantes

Usar MAYUSCULAS.

Ejemplos:

```python
SECRET_KEY
ALGORITHM
DATABASE_URL
```

---

# Base de datos

## ORM

Siempre utilizar SQLAlchemy ORM.

No escribir SQL crudo salvo necesidad extrema.

Correcto:

```python
db.query(models.Usuario)
```

Incorrecto:

```python
db.execute(
    "SELECT * FROM usuarios"
)
```

---

## Relaciones

Usar siempre relationships cuando existan.

Ejemplo:

```python
prediccion.usuario
prediccion.partido
```

---

# FastAPI

## Organización

Actualmente toda la API vive en:

```text
app/main.py
```

No crear carpetas nuevas ni reorganizar la arquitectura sin aprobación explícita.

NO crear:

```text
services/
repositories/
controllers/
```

porque no forman parte de la arquitectura actual.

---

## Dependencias

Utilizar:

```python
Depends(get_db)
```

para acceso a base de datos.

---

## Errores

Siempre usar HTTPException.

Ejemplo:

```python
raise HTTPException(
    status_code=404,
    detail="Partido no encontrado"
)
```

---

# Formato de respuestas

Mantener compatibilidad con la API existente.

Ejemplos:

```python
{
    "mensaje": "Predicción registrada"
}
```

```python
{
    "partido_id": 1
}
```

```python
{
    "access_token": "...",
    "token_type": "bearer"
}
```

No introducir wrappers globales como:

```python
{
    "data": ...
}
```

o

```python
{
    "success": true
}
```

sin una refactorización completa del proyecto.

---

# Autenticación

La autenticación utiliza:

```text
?token=JWT
```

como query parameter.

No migrar a:

```text
Authorization: Bearer
```

a menos que el proyecto lo solicite explícitamente.

---

# Docker

## Servicios oficiales

Los nombres válidos son:

```text
db
app1
app2
app3
nginx
```

No cambiar nombres de servicios.

---

## Base de datos

La conexión siempre debe obtenerse desde:

```text
DATABASE_URL
```

mediante variables de entorno.

Nunca hardcodear hosts.

Correcto:

```python
os.getenv("DATABASE_URL")
```

Incorrecto:

```python
postgresql://localhost
```

---

# Logging

Usar print() únicamente para depuración temporal.

No dejar prints innecesarios en commits finales.

---

# Frontend

Frontend permitido:

```text
HTML
CSS
JavaScript Vanilla
```

No agregar:

* React
* Vue
* Angular
* jQuery

---

# Testing

Stress testing:

```text
Locust
```

Archivo oficial:

```text
tests/locustfile.py
```

---

# Commits

Formato:

```text
feat: nueva funcionalidad
fix: corrección de error
docs: documentación
test: pruebas
refactor: reorganización interna
docker: cambios de infraestructura
```

Ejemplos:

```text
feat: add match creation endpoint

fix: prevent duplicate predictions

docs: update architecture

docker: add nginx load balancer
```

---

# Regla para IA

Antes de generar código:

1. Leer ARCHITECTURE.md
2. Respetar esta guía
3. Mantener compatibilidad con endpoints existentes
4. No introducir nuevas arquitecturas
5. No cambiar contratos de API existentes
6. No cambiar nombres de tablas existentes
7. No cambiar reglas de puntuación existentes
