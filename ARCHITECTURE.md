# ARCHITECTURE.md — Sistema de Predicciones del Mundial

> Plano del proyecto. Lee esto antes de generar cualquier código.

---

## ¿Qué hace este sistema?

Aplicación web donde usuarios registrados predicen marcadores de partidos del Mundial. Se organizan en **salas privadas** con código de invitación. El sistema calcula puntos automáticamente según 5 reglas al registrar el resultado real.

---

## Stack tecnológico

| Capa | Tecnología |
|------|------------|
| Backend | Python 3 + FastAPI |
| Base de datos | PostgreSQL (única, compartida) |
| Load Balancer | Nginx |
| Contenedores | Docker + Docker Compose |
| Frontend | HTML + CSS + JavaScript puro (sin frameworks) |
| Tests de carga | Locust |

---

## Estructura de carpetas

```
futbol-predicciones/
├── app/
│   ├── main.py          # API principal — todos los endpoints REST
│   ├── models.py        # Modelos SQLAlchemy (tablas de BD)
│   ├── database.py      # Conexión y sesión con PostgreSQL
│   ├── schemas.py       # Validación de datos entrada/salida (Pydantic)
│   ├── scoring.py       # Lógica de las 5 reglas de puntuación
│   └── static/
│       ├── index.html   # Pantalla: Login / Registro
│       ├── salas.html   # Pantalla: Mis Salas (crear / unirse)
│       ├── partidos.html # Pantalla: Partidos y predicciones
│       └── ranking.html  # Pantalla: Ranking de sala
├── nginx/
│   └── nginx.conf       # Balanceo de carga: app1, app2, app3
├── tests/
│   └── locustfile.py    # Stress testing con Locust
├── Dockerfile           # Imagen del contenedor FastAPI
├── docker-compose.yml   # Orquestación: 3x app + PostgreSQL + Nginx
└── requirements.txt
```

---

## Servicios Docker (docker-compose)

```
Internet → Nginx (puerto 80)
              ↓  round-robin
    ┌─────────┬─────────┐
   app1      app2      app3      ← 3 instancias FastAPI (puerto 8000 interno)
    └─────────┴────┬────┘
                   ↓
             PostgreSQL (puerto 5432 interno)
```

- **app1 / app2 / app3**: misma imagen, variable `APP_INSTANCE` diferente
- **db**: PostgreSQL, volumen persistente `postgres_data`
- **nginx**: upstream con `least_conn`, health checks pasivos

---

## Modelos de base de datos

### `usuarios`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer PK | Auto-incremental |
| nombre | String UNIQUE | Nombre de usuario |
| password | String | Hash bcrypt |

### `salas`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer PK | Auto-incremental |
| nombre | String | Nombre visible |
| codigo | String(6) UNIQUE | Código de invitación |
| creador_id | FK → usuarios | Quién puede crear partidos y registrar resultados |

### `sala_usuarios`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer PK | |
| sala_id | FK → salas | |
| usuario_id | FK → usuarios | |
| puntos_total | Integer | Puntaje acumulado en esta sala |

### `partidos`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer PK | |
| sala_id | FK → salas | |
| equipo_local | String | |
| equipo_visitante | String | |
| fecha_partido | DateTime | Para calcular bonus anticipado |
| goles_local | Integer nullable | Resultado real |
| goles_visitante | Integer nullable | Resultado real |
| finalizado | Boolean | Si True, bloquea nuevas predicciones |

### `predicciones`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer PK | |
| usuario_id | FK → usuarios | |
| partido_id | FK → partidos | |
| goles_local | Integer | Predicción del usuario |
| goles_visitante | Integer | Predicción del usuario |
| puntos | Integer | Calculado al registrar resultado |
| fecha_prediccion | DateTime | Para R5: bonus anticipado (+24h) |

---

## Endpoints de la API

**Autenticación**: todos los endpoints protegidos reciben `?token=TU_TOKEN` en la URL (query param).

### Autenticación
| Método | Ruta | Body | Respuesta |
|--------|------|------|-----------|
| POST | `/registro` | `{"nombre": "...", "password": "..."}` | `{"access_token": "...", "token_type": "bearer"}` |
| POST | `/login` | `{"nombre": "...", "password": "..."}` | `{"access_token": "...", "token_type": "bearer"}` |

### Salas
| Método | Ruta | Body | Respuesta |
|--------|------|------|-----------|
| POST | `/salas?token=...` | `{"nombre": "Mi Sala"}` | `{"sala_id": 1, "codigo": "AB3X9K", "nombre": "Mi Sala"}` |
| POST | `/salas/unirse?token=...` | `{"codigo": "AB3X9K"}` | `{"mensaje": "Te uniste a la sala Mi Sala"}` |
| GET | `/salas/{id}/ranking` | — | `[{"usuario": "juan", "puntos": 10}]` |
| GET | `/salas/{id}/partidos` | — | `[{"id": 1, "equipo_local": "Francia", ...}]` |

### Partidos
| Método | Ruta | Body | Respuesta |
|--------|------|------|-----------|
| POST | `/salas/{id}/partidos?token=...` | `{"equipo_local": "...", "equipo_visitante": "...", "fecha_partido": "2026-06-20T20:00:00"}` | `{"partido_id": 1}` |
| POST | `/partidos/{id}/resultado?token=...` | `{"goles_local": 2, "goles_visitante": 1}` | `{"mensaje": "Resultado registrado y puntos calculados"}` |

### Predicciones
| Método | Ruta | Body | Respuesta |
|--------|------|------|-----------|
| POST | `/partidos/{id}/predicciones?token=...` | `{"goles_local": 2, "goles_visitante": 1}` | `{"mensaje": "Prediccion registrada"}` |

### Códigos de error
| Código | Cuándo |
|--------|--------|
| 400 | Usuario ya existe / ya predijo / partido finalizado / ya es miembro |
| 401 | Token inválido o ausente |
| 403 | No es el creador de la sala |
| 404 | Sala o partido no encontrado |

---

## Sistema de puntuación (scoring.py)

| Regla | Condición | Puntos |
|-------|-----------|--------|
| R1 — Exacto | Marcador exacto correcto | +5 |
| R2 — Ganador | Ganador o empate correcto (sin exacto) | +3 |
| R3 — Diferencia | Margen de goles correcto (sin exacto) | +2 |
| R4 — Racha | Cada 3 partidos consecutivos con ganador correcto | +2 extra |
| R5 — Anticipada | Predicción registrada >24h antes del partido | +1 extra |

La función en `scoring.py` recibe `(prediccion, resultado_real)` y retorna los puntos. Se llama desde `POST /partidos/{id}/resultado` para cada predicción del partido.

---

## Frontend (app/static/)

Cada archivo HTML es una SPA independiente. Usan `fetch()` nativo sin jQuery ni React. El token se guarda en `localStorage` como `access_token`.

| Archivo | Ruta de acceso | Endpoints que consume |
|---------|---------------|----------------------|
| index.html | `/` | POST /registro, POST /login |
| salas.html | `/static/salas.html` | POST /salas, POST /salas/unirse, GET /salas/{id}/partidos |
| partidos.html | `/static/partidos.html` | GET /salas/{id}/partidos, POST /partidos/{id}/predicciones |
| ranking.html | `/static/ranking.html` | GET /salas/{id}/ranking |

FastAPI sirve los estáticos automáticamente con `StaticFiles` montado en `/static`.