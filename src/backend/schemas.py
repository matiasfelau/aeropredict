"""
Schemas Pydantic para validación de request/response en endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ============================================================================
# AUTH
# ============================================================================


class LoginRequest(BaseModel):
    """Request para POST /auth/login."""

    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """Response de login con JWT token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


class UsuarioResponse(BaseModel):
    """Response de usuario (sin password)."""

    id: int
    username: str
    email: str
    activo: bool
    creado_en: datetime

    class Config:
        from_attributes = True


# ============================================================================
# RUTAS
# ============================================================================


class RutaBase(BaseModel):
    """Base para ruta (campos comunes)."""

    anio: int = Field(..., ge=2017)
    mes: int = Field(..., ge=1, le=12)
    ruta: str
    clasificacion_vuelo: str
    origen_localidad: str
    origen_provincia: str
    destino_localidad: str
    destino_provincia: str
    pasajeros: int = Field(..., ge=0)
    asientos: int = Field(..., ge=0)
    vuelos: int = Field(..., ge=0)
    factor_ocupacion: float = Field(..., ge=0, le=1.05)


class RutaCreate(RutaBase):
    """Request para crear ruta (POST)."""

    pass


class RutaUpdate(BaseModel):
    """Request para actualizar ruta (PATCH)."""

    pasajeros: Optional[int] = None
    asientos: Optional[int] = None
    vuelos: Optional[int] = None
    factor_ocupacion: Optional[float] = None


class RutaResponse(RutaBase):
    """Response de ruta desde GET."""

    id: int
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


# ============================================================================
# RUTAS AEROLÍNEA
# ============================================================================


class RutaAerolineaBase(BaseModel):
    """Base para ruta desglosada por aerolínea."""

    aerolinea: str
    pasajeros: int = Field(..., ge=0)
    asientos: int = Field(..., ge=0)
    vuelos: int = Field(..., ge=0)
    factor_ocupacion: float = Field(..., ge=0, le=1.05)


class RutaAerolineaResponse(RutaAerolineaBase):
    """Response de ruta + aerolínea."""

    id: int
    ruta_id: int
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


class RutaConAerolineas(RutaResponse):
    """Response de ruta con sus desglos por aerolínea."""

    rutas_aerolinea: list[RutaAerolineaResponse] = []


# ============================================================================
# AEROPUERTOS
# ============================================================================


class AeropuertoBase(BaseModel):
    """Base para aeropuerto."""

    codigo_oaci: str = Field(..., min_length=4, max_length=10)
    nombre: str
    localidad: str
    provincia: str
    pais: str = "Argentina"
    latitud: Optional[float] = None
    longitud: Optional[float] = None


class AeropuertoResponse(AeropuertoBase):
    """Response de aeropuerto."""

    id: int
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


# ============================================================================
# REPORTES Y ANÁLISIS
# ============================================================================


class OcupacionPorRuta(BaseModel):
    """Ocupación de una ruta en un período."""

    ruta: str
    anio: int
    mes: int
    factor_ocupacion: float
    pasajeros: int
    asientos: int
    vuelos: int


class TendenciaRuta(BaseModel):
    """Tendencia de una ruta en últimos N meses."""

    anio: int
    mes: int
    factor_ocupacion: float
    pasajeros: int
    asientos: int


class AlertaOcupacion(BaseModel):
    """Alerta de ocupación baja o elevada."""

    ruta: str
    tipo: str = Field(..., pattern="^(baja|elevada)$")
    factor_ocupacion: float
    umbral: float
    anio: int
    mes: int


class RutaTopTrafic(BaseModel):
    """Ruta con mayor tráfico."""

    ruta: str
    pasajeros_total: int
    factor_ocupacion_promedio: float


class ParticipacionAerolinea(BaseModel):
    """Participación de una aerolínea."""

    aerolinea: str
    pasajeros_total: int
    vuelos_total: int
    factor_ocupacion_promedio: float
    porcentaje_mercado: float  # 0-100


class ReporteCalidadResponse(BaseModel):
    """Response de reporte de calidad del pipeline."""

    id: int
    fecha_generacion: datetime
    total_registros: int
    total_descartados: int
    rutas_unicas: int
    aerolineas_unicas: int
    periodo_inicio: Optional[str] = None
    periodo_fin: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# PAGINATION
# ============================================================================


class PaginatedResponse(BaseModel):
    """Response genérico paginado."""

    total: int
    limit: int
    offset: int
    items: list = []


# ============================================================================
# ADMIN
# ============================================================================


class DataLoadResponse(BaseModel):
    """Response de carga/recarga de datos."""

    exitoso: bool
    timestamp: datetime
    rutas_nuevas: int
    rutas_actualizadas: int
    aeropuertos_nuevos: int
    aeropuertos_actualizados: int
    errores: list[str] = []


class SyncMetadataResponse(BaseModel):
    """Metadata del último sync con el pipeline."""

    ultimo_sync: Optional[datetime]
    rutas_totales: int
    aeropuertos_totales: int
    reporte_calidad_mas_reciente: Optional[ReporteCalidadResponse]


# ============================================================================
# PREDICCIONES (IA)
# ============================================================================


class PrediccionRequest(BaseModel):
    """Request para consultar una predicción de demanda u ocupación."""

    origen_localidad: str = Field(..., min_length=2, max_length=255)
    destino_localidad: str = Field(..., min_length=2, max_length=255)
    anio: int = Field(..., ge=2017)
    mes: int = Field(..., ge=1, le=12)
    clasificacion_vuelo: str = Field(..., pattern="^(cabotaje|internacional)$")
    asientos: Optional[int] = Field(None, ge=0)
    vuelos: Optional[int] = Field(None, ge=0)


class DemandaResponse(BaseModel):
    """Response con pasajeros estimados y nivel de demanda."""

    ruta: str
    pasajeros_predichos: int
    nivel_demanda: str
    alerta: str
    recomendacion: str


class OcupacionResponse(BaseModel):
    """Response con pasajeros y factor de ocupación estimado."""

    ruta: str
    pasajeros_predichos: int
    asientos: int
    ocupacion_predicha: float
    nivel_ocupacion: str
    alerta: str
    recomendacion: str


class ModelMetricasResponse(BaseModel):
    """Response con las métricas técnicas del modelo entrenado."""

    modelo: str
    variable_objetivo: str
    registros_entrenamiento: int
    registros_prueba: int
    mae: float
    rmse: float
    mape: float
    r2: float
    fecha_entrenamiento: str
    variables_usadas: list[str]
    tiempo_entrenamiento_seg: float

