from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    password = Column(String)
    predicciones = relationship("Prediccion", back_populates="usuario")
    salas = relationship("SalaUsuario", back_populates="usuario")

class Sala(Base):
    __tablename__ = "salas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    codigo = Column(String, unique=True, index=True)
    creador_id = Column(Integer, ForeignKey("usuarios.id"))
    partidos = relationship("Partido", back_populates="sala")
    miembros = relationship("SalaUsuario", back_populates="sala")

class SalaUsuario(Base):
    __tablename__ = "sala_usuarios"
    id = Column(Integer, primary_key=True, index=True)
    sala_id = Column(Integer, ForeignKey("salas.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    puntos_total = Column(Integer, default=0)
    sala = relationship("Sala", back_populates="miembros")
    usuario = relationship("Usuario", back_populates="salas")

class Partido(Base):
    __tablename__ = "partidos"
    id = Column(Integer, primary_key=True, index=True)
    sala_id = Column(Integer, ForeignKey("salas.id"))
    equipo_local = Column(String)
    equipo_visitante = Column(String)
    fecha_partido = Column(DateTime)
    goles_local = Column(Integer, nullable=True)
    goles_visitante = Column(Integer, nullable=True)
    finalizado = Column(Boolean, default=False)
    sala = relationship("Sala", back_populates="partidos")
    predicciones = relationship("Prediccion", back_populates="partido")

class Prediccion(Base):
    __tablename__ = "predicciones"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    partido_id = Column(Integer, ForeignKey("partidos.id"))
    goles_local = Column(Integer)
    goles_visitante = Column(Integer)
    puntos = Column(Integer, default=0)
    fecha_prediccion = Column(DateTime, default=datetime.utcnow)
    usuario = relationship("Usuario", back_populates="predicciones")
    partido = relationship("Partido", back_populates="predicciones")