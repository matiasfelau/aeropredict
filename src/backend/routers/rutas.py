"""
Router de rutas aéreas.

Endpoints:
- GET /api/rutas — listar rutas con paginación
- GET /api/rutas/{id} — obtener detalle de ruta
- GET /api/rutas/buscar — búsqueda avanzada con filtros
- GET /api/rutas/ruta/{nombre_ruta} — búsqueda por nombre de ruta
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Ruta
from ..schemas import RutaResponse, RutaConAerolineas, PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def listar_rutas(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Lista todas las rutas con paginación.

    Query params:
    - limit: Número de resultados (default 20, max 100)
    - offset: Desplazamiento (default 0)

    Returns:
        PaginatedResponse con total, limit, offset e items
    """
    total = db.query(Ruta).count()
    items = db.query(Ruta).offset(offset).limit(limit).all()

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[RutaResponse.model_validate(item) for item in items],
    )


@router.get("/{ruta_id}", response_model=RutaConAerolineas)
async def obtener_ruta(
    ruta_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Obtiene los detalles de una ruta incluyendo sus desglos por aerolínea.

    Args:
        ruta_id: ID de la ruta

    Returns:
        RutaConAerolineas con datos de la ruta y lista de rutas_aerolinea

    Raises:
        404: Si la ruta no existe
    """
    ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()

    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ruta con ID {ruta_id} no encontrada",
        )

    return RutaConAerolineas.model_validate(ruta)


@router.get("/buscar/avanzada", response_model=PaginatedResponse)
async def buscar_rutas_avanzada(
    db: Annotated[Session, Depends(get_db)],
    anio: Optional[int] = Query(None, ge=2017),
    mes: Optional[int] = Query(None, ge=1, le=12),
    aerolinea: Optional[str] = Query(None),
    origen_localidad: Optional[str] = Query(None),
    destino_localidad: Optional[str] = Query(None),
    factor_min: Optional[float] = Query(None, ge=0, le=1.05),
    factor_max: Optional[float] = Query(None, ge=0, le=1.05),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Búsqueda avanzada de rutas con múltiples filtros.

    Query params (todos opcionales):
    - anio: Año (>= 2017)
    - mes: Mes (1-12)
    - aerolinea: Nombre de la aerolínea
    - origen_localidad: Localidad de origen
    - destino_localidad: Localidad de destino
    - factor_min: Factor de ocupación mínimo (0-1.05)
    - factor_max: Factor de ocupación máximo (0-1.05)
    - limit: Número de resultados (default 20)
    - offset: Desplazamiento (default 0)

    Returns:
        PaginatedResponse con rutas filtradas
    """
    query = db.query(Ruta)

    # Aplicar filtros
    if anio is not None:
        query = query.filter(Ruta.anio == anio)
    if mes is not None:
        query = query.filter(Ruta.mes == mes)
    if origen_localidad:
        query = query.filter(
            Ruta.origen_localidad.ilike(f"%{origen_localidad}%")
        )
    if destino_localidad:
        query = query.filter(
            Ruta.destino_localidad.ilike(f"%{destino_localidad}%")
        )
    if factor_min is not None:
        query = query.filter(Ruta.factor_ocupacion >= factor_min)
    if factor_max is not None:
        query = query.filter(Ruta.factor_ocupacion <= factor_max)

    # Filtro por aerolínea (requiere join con RutaAerolinea)
    if aerolinea:
        query = query.join(Ruta.rutas_aerolinea).filter(
            Ruta.rutas_aerolinea.any(Ruta.rutas_aerolinea.ilike(f"%{aerolinea}%"))
        )

    total = query.count()
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[RutaResponse.model_validate(item) for item in items],
    )


@router.get("/ruta/{nombre_ruta}", response_model=PaginatedResponse)
async def buscar_por_nombre_ruta(
    nombre_ruta: str,
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Búsqueda de rutas por nombre de ruta.
    Ej: "Buenos Aires - Bariloche"

    Args:
        nombre_ruta: Nombre de la ruta (búsqueda parcial)
        limit: Número de resultados
        offset: Desplazamiento

    Returns:
        PaginatedResponse con rutas que coincidan
    """
    query = db.query(Ruta).filter(Ruta.ruta.ilike(f"%{nombre_ruta}%"))
    total = query.count()
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[RutaResponse.model_validate(item) for item in items],
    )
