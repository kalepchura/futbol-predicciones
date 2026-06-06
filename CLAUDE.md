# CLAUDE.md — Contexto del proyecto para Claude Code

> Este archivo se carga automáticamente en cada sesión. No modificar sin consenso del equipo.

## Proyecto

Aplicación web de predicciones del Mundial de fútbol. Usuarios registrados predicen marcadores, se organizan en salas privadas con código de invitación, y acumulan puntos automáticamente según 5 reglas.

## Stack

- Backend: Python 3.11 + FastAPI — `app/main.py` (todos los endpoints)
- Base de datos: PostgreSQL 15 + SQLAlchemy ORM — `app/models.py`
- Frontend: HTML + CSS + JavaScript Vanilla — `app/static/`
- Infraestructura: Docker Compose + Nginx (3 instancias FastAPI con round-robin)
- Tests de carga: Locust — `tests/locustfile.py`

## Reglas críticas

1. TODO el código en inglés. Mensajes al usuario en español.
2. Frontend: solo HTML, CSS, JS Vanilla. PROHIBIDO React, Vue, jQuery, Angular.
3. Toda la API vive en `app/main.py`. No crear `services/`, `repositories/`, `controllers/`.
4. Autenticación: `?token=JWT` como query parameter (no Authorization header).
5. No cambiar contratos de API, nombres de tablas, ni reglas de puntuación.
6. ORM siempre (SQLAlchemy). No SQL crudo.
7. Errores: siempre `HTTPException`.
8. Commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `docker:`
9. Ramas: trabajar en `feature/frontend`, integrar a `dev`, nunca directo a `main`.

## Estructura de carpetas

```
app/
  main.py        # Todos los endpoints REST
  models.py      # Tablas: usuarios, salas, sala_usuarios, partidos, predicciones
  database.py    # Sesión PostgreSQL
  schemas.py     # Pydantic
  scoring.py     # 5 reglas de puntuación
  static/
    index.html   # Login / Registro  →  POST /registro, POST /login
    salas.html   # Salas            →  POST /salas, POST /salas/unirse, GET /salas/{id}/partidos
    partidos.html # Predicciones    →  GET /salas/{id}/partidos, POST /partidos/{id}/predicciones
    ranking.html  # Ranking         →  GET /salas/{id}/ranking
nginx/nginx.conf
tests/locustfile.py
```

## Endpoints (resumen)

| Método | Ruta | Auth |
|--------|------|------|
| POST | `/registro` | No |
| POST | `/login` | No |
| POST | `/salas` | ?token |
| POST | `/salas/unirse` | ?token |
| GET | `/salas/{id}/ranking` | No |
| GET | `/salas/{id}/partidos` | No |
| POST | `/salas/{id}/partidos` | ?token (solo creador) |
| POST | `/partidos/{id}/resultado` | ?token (solo creador) |
| POST | `/partidos/{id}/predicciones` | ?token |

## Respuestas API (no cambiar formato)

```json
{"access_token": "...", "token_type": "bearer"}
{"sala_id": 1, "codigo": "AB3X9K", "nombre": "Mi Sala"}
{"mensaje": "Predicción registrada"}
{"partido_id": 1}
```

## Frontend — patrón obligatorio

```javascript
// Token siempre en localStorage
const token = localStorage.getItem('access_token');

// Llamadas con token como query param
fetch(`/salas?token=${token}`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(data)
})
```

## Puntuación (NO modificar lógica)

- R1 Exacto: +5 pts (marcador exacto)
- R2 Ganador: +3 pts (equipo correcto sin exacto)
- R3 Diferencia: +2 pts (margen correcto sin exacto)
- R4 Racha: +2 pts extra (cada 3 partidos consecutivos acertados)
- R5 Anticipada: +1 pt extra (predicción >24h antes del partido)

## Docker — servicios válidos

`db`, `app1`, `app2`, `app3`, `nginx`. No cambiar nombres.
