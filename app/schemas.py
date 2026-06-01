from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str
    password: str

class UsuarioLogin(BaseModel):
    nombre: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class SalaCreate(BaseModel):
    nombre: str

class SalaUnirse(BaseModel):
    codigo: str

class PartidoCreate(BaseModel):
    equipo_local: str
    equipo_visitante: str
    fecha_partido: datetime

class ResultadoCreate(BaseModel):
    goles_local: int
    goles_visitante: int

class PrediccionCreate(BaseModel):
    goles_local: int
    goles_visitante: int