"""
Modelos ORM SQLAlchemy para AeroPredict.

Tablas:
- usuarios: autenticación
- rutas: datos mensales por ruta
- rutas_aerolinea: datos mensales por ruta + aerolínea
- aeropuertos: catálogo de aeropuertos
- reportes_calidad: metadatos de reportes generados
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
    Boolean,
)
from sqlalchemy.orm import relationship

from .database import Base


class Usuario(Base):
    """Tabla de usuarios para autenticación JWT."""

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)


class Ruta(Base):
    """Tabla de rutas con datos mensales agregados."""

    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, index=True)
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    ruta = Column(String(255), nullable=False)  # "Buenos Aires - Bariloche"
    clasificacion_vuelo = Column(String(50), nullable=False)
    origen_localidad = Column(String(255), nullable=False)
    origen_provincia = Column(String(255), nullable=False)
    destino_localidad = Column(String(255), nullable=False)
    destino_provincia = Column(String(255), nullable=False)
    pasajeros = Column(Integer, nullable=False)
    asientos = Column(Integer, nullable=False)
    vuelos = Column(Integer, nullable=False)
    factor_ocupacion = Column(Float, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    rutas_aerolinea = relationship("RutaAerolinea", back_populates="ruta", cascade="all, delete-orphan")

    # Índices para búsquedas rápidas
    __table_args__ = (
        Index("ix_rutas_anio_mes_ruta", "anio", "mes", "ruta"),
        Index("ix_rutas_anio_mes", "anio", "mes"),
        Index("ix_rutas_origen", "origen_localidad", "origen_provincia"),
        Index("ix_rutas_destino", "destino_localidad", "destino_provincia"),
        UniqueConstraint("anio", "mes", "ruta", "clasificacion_vuelo", name="uq_rutas_key"),
    )


class RutaAerolinea(Base):
    """Tabla de rutas desglosadas por aerolínea."""

    __tablename__ = "rutas_aerolinea"

    id = Column(Integer, primary_key=True, index=True)
    ruta_id = Column(Integer, ForeignKey("rutas.id"), nullable=False)
    aerolinea = Column(String(255), nullable=False)
    pasajeros = Column(Integer, nullable=False)
    asientos = Column(Integer, nullable=False)
    vuelos = Column(Integer, nullable=False)
    factor_ocupacion = Column(Float, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    ruta = relationship("Ruta", back_populates="rutas_aerolinea")

    # Índices
    __table_args__ = (
        Index("ix_rutas_aerolinea_aerolinea", "aerolinea"),
        Index("ix_rutas_aerolinea_ruta_id", "ruta_id"),
        UniqueConstraint("ruta_id", "aerolinea", name="uq_ruta_aerolinea"),
    )


class Aeropuerto(Base):
    """Tabla de catálogo de aeropuertos."""

    __tablename__ = "aeropuertos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_oaci = Column(String(10), unique=True, index=True, nullable=False)  # e.g. SABE, SAEZ
    nombre = Column(String(255), nullable=False)
    localidad = Column(String(255), nullable=False)
    provincia = Column(String(255), nullable=False)
    pais = Column(String(100), nullable=False, default="Argentina")
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Índices
    __table_args__ = (
        Index("ix_aeropuertos_localidad", "localidad"),
        Index("ix_aeropuertos_provincia", "provincia"),
    )


class ReporteCalidad(Base):
    """Tabla de metadatos de reportes de calidad generados por el pipeline."""

    __tablename__ = "reportes_calidad"

    id = Column(Integer, primary_key=True, index=True)
    fecha_generacion = Column(DateTime, nullable=False)
    total_registros = Column(Integer, nullable=False)
    total_descartados = Column(Integer, nullable=False)
    descartes_por_regla = Column(Text, nullable=True)  # JSON serializado
    rutas_unicas = Column(Integer, nullable=False)
    aerolineas_unicas = Column(Integer, nullable=False)
    periodo_inicio = Column(Date, nullable=True)
    periodo_fin = Column(Date, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_reportes_calidad_fecha", "fecha_generacion"),
    )
