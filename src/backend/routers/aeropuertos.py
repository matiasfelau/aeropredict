"""
Router de aeropuertos.

Endpoints:
- GET /api/aeropuertos — listar aeropuertos
- GET /api/aeropuertos/{codigo_oaci} — obtener detalle de aeropuerto
- GET /api/aeropuertos/buscar — búsqueda avanzada de aeropuertos
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Aeropuerto
from ..schemas import AeropuertoResponse, PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def listar_aeropuertos(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Lista todos los aeropuertos con paginación.

    Query params:
    - limit: Número de resultados (default 50, max 200)
    - offset: Desplazamiento (default 0)

    Returns:
        PaginatedResponse con total, limit, offset e items
    """
    total = db.query(Aeropuerto).count()
    items = db.query(Aeropuerto).offset(offset).limit(limit).all()

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[AeropuertoResponse.model_validate(item) for item in items],
    )


@router.get("/{codigo_oaci}", response_model=AeropuertoResponse)
async def obtener_aeropuerto(
    codigo_oaci: str,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Obtiene los detalles de un aeropuerto por su código OACI.

    Args:
        codigo_oaci: Código OACI en mayúscula (ej: SABE, SAEZ)

    Returns:
        AeropuertoResponse con datos del aeropuerto

    Raises:
        404: Si el aeropuerto no existe
    """
    # Normalizar código a mayúsculas
    codigo_oaci = codigo_oaci.upper()

    aeropuerto = (
        db.query(Aeropuerto)
        .filter(Aeropuerto.codigo_oaci == codigo_oaci)
        .first()
    )

    if not aeropuerto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aeropuerto {codigo_oaci} no encontrado",
        )

    return AeropuertoResponse.model_validate(aeropuerto)


@router.get("/buscar/avanzada", response_model=PaginatedResponse)
async def buscar_aeropuertos_avanzada(
    db: Annotated[Session, Depends(get_db)],
    nombre: Optional[str] = Query(None),
    localidad: Optional[str] = Query(None),
    provincia: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Búsqueda avanzada de aeropuertos con múltiples filtros.

    Query params (todos opcionales):
    - nombre: Nombre del aeropuerto (búsqueda parcial)
    - localidad: Localidad (búsqueda parcial)
    - provincia: Provincia (búsqueda parcial)
    - limit: Número de resultados (default 50)
    - offset: Desplazamiento (default 0)

    Returns:
        PaginatedResponse con aeropuertos filtrados
    """
    query = db.query(Aeropuerto)

    if nombre:
        query = query.filter(Aeropuerto.nombre.ilike(f"%{nombre}%"))
    if localidad:
        query = query.filter(Aeropuerto.localidad.ilike(f"%{localidad}%"))
    if provincia:
        query = query.filter(Aeropuerto.provincia.ilike(f"%{provincia}%"))

    total = query.count()
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[AeropuertoResponse.model_validate(item) for item in items],
    )
