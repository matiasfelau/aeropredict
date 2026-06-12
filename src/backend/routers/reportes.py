"""
Router de reportes y análisis.

Endpoints:
- GET /api/reportes/ocupacion — ocupación por ruta en un período
- GET /api/reportes/tendencias — tendencias de una ruta
- GET /api/reportes/alertas — rutas con ocupación baja/elevada
- GET /api/reportes/top-rutas — rutas con mayor tráfico
- GET /api/reportes/aerolineas — participación por aerolínea
"""

from typing import Annotated, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Ruta, RutaAerolinea
from ..schemas import (
    OcupacionPorRuta,
    TendenciaRuta,
    AlertaOcupacion,
    RutaTopTrafic,
    ParticipacionAerolinea,
    PaginatedResponse,
)

router = APIRouter()


@router.get("/ocupacion", response_model=PaginatedResponse)
async def reportar_ocupacion(
    db: Annotated[Session, Depends(get_db)],
    anio: int = Query(..., ge=2017),
    mes: int = Query(..., ge=1, le=12),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Reporte de ocupación por ruta en un período específico.

    Query params:
    - anio: Año (requerido)
    - mes: Mes (requerido)
    - limit: Número de resultados (default 50)
    - offset: Desplazamiento (default 0)

    Returns:
        PaginatedResponse con lista de OcupacionPorRuta
    """
    query = db.query(Ruta).filter(
        (Ruta.anio == anio) & (Ruta.mes == mes)
    )

    total = query.count()
    items = query.offset(offset).limit(limit).all()

    ocupaciones = [
        OcupacionPorRuta(
            ruta=item.ruta,
            anio=item.anio,
            mes=item.mes,
            factor_ocupacion=item.factor_ocupacion,
            pasajeros=item.pasajeros,
            asientos=item.asientos,
            vuelos=item.vuelos,
        )
        for item in items
    ]

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=ocupaciones,
    )


@router.get("/tendencias", response_model=list[TendenciaRuta])
async def obtener_tendencias(
    db: Annotated[Session, Depends(get_db)],
    ruta: str = Query(..., min_length=1),
    meses: int = Query(12, ge=1, le=60),
):
    """
    Obtiene la tendencia de una ruta en los últimos N meses.

    Query params:
    - ruta: Nombre de la ruta (requerido)
    - meses: Número de meses a consultar (default 12, max 60)

    Returns:
        Lista de TendenciaRuta ordenada cronológicamente
    """
    items = (
        db.query(Ruta)
        .filter(Ruta.ruta.ilike(f"%{ruta}%"))
        .order_by(desc(Ruta.anio), desc(Ruta.mes))
        .limit(meses)
        .all()
    )

    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron datos para la ruta '{ruta}'",
        )

    tendencias = [
        TendenciaRuta(
            anio=item.anio,
            mes=item.mes,
            factor_ocupacion=item.factor_ocupacion,
            pasajeros=item.pasajeros,
            asientos=item.asientos,
        )
        for item in reversed(items)  # Orden cronológico ascendente
    ]

    return tendencias


@router.get("/alertas", response_model=list[AlertaOcupacion])
async def obtener_alertas(
    db: Annotated[Session, Depends(get_db)],
    limite: int = Query(100, ge=1, le=1000),
):
    """
    Retorna rutas con ocupación baja (< UMBRAL_BAJA_OCUPACION) o
    elevada (> UMBRAL_OCUPACION_ELEVADA).

    Query params:
    - limite: Número máximo de alertas a retornar (default 100)

    Returns:
        Lista de AlertaOcupacion ordenada por factor de ocupación
    """
    # Rutas con ocupación baja
    bajas = db.query(Ruta).filter(
        Ruta.factor_ocupacion < settings.UMBRAL_BAJA_OCUPACION
    ).all()

    # Rutas con ocupación elevada
    elevadas = db.query(Ruta).filter(
        Ruta.factor_ocupacion > settings.UMBRAL_OCUPACION_ELEVADA
    ).all()

    alertas = []

    for item in bajas:
        alertas.append(
            AlertaOcupacion(
                ruta=item.ruta,
                tipo="baja",
                factor_ocupacion=item.factor_ocupacion,
                umbral=settings.UMBRAL_BAJA_OCUPACION,
                anio=item.anio,
                mes=item.mes,
            )
        )

    for item in elevadas:
        alertas.append(
            AlertaOcupacion(
                ruta=item.ruta,
                tipo="elevada",
                factor_ocupacion=item.factor_ocupacion,
                umbral=settings.UMBRAL_OCUPACION_ELEVADA,
                anio=item.anio,
                mes=item.mes,
            )
        )

    # Ordenar y limitar
    alertas = sorted(alertas, key=lambda x: x.factor_ocupacion)
    return alertas[:limite]


@router.get("/top-rutas", response_model=list[RutaTopTrafic])
async def obtener_top_rutas(
    db: Annotated[Session, Depends(get_db)],
    periodo: str = Query("mes", regex="^(mes|anio)$"),
    anio: Optional[int] = Query(None, ge=2017),
    mes: Optional[int] = Query(None, ge=1, le=12),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Obtiene las rutas con mayor tráfico (pasajeros totales).

    Query params:
    - periodo: "mes" (requiere anio y mes) o "anio" (requiere anio)
    - anio: Año (requerido)
    - mes: Mes (requerido si periodo=mes)
    - limit: Número de rutas a retornar (default 10)

    Returns:
        Lista de RutaTopTrafic ordenada por pasajeros totales
    """
    query = db.query(
        Ruta.ruta,
        func.sum(Ruta.pasajeros).label("pasajeros_total"),
        func.avg(Ruta.factor_ocupacion).label("factor_ocupacion_promedio"),
    ).group_by(Ruta.ruta)

    if periodo == "mes":
        if anio is None or mes is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="anio y mes son requeridos cuando periodo=mes",
            )
        query = query.filter((Ruta.anio == anio) & (Ruta.mes == mes))
    elif periodo == "anio":
        if anio is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="anio es requerido cuando periodo=anio",
            )
        query = query.filter(Ruta.anio == anio)

    items = (
        query.order_by(desc("pasajeros_total"))
        .limit(limit)
        .all()
    )

    top_rutas = [
        RutaTopTrafic(
            ruta=item.ruta,
            pasajeros_total=int(item.pasajeros_total),
            factor_ocupacion_promedio=float(item.factor_ocupacion_promedio),
        )
        for item in items
    ]

    return top_rutas


@router.get("/aerolineas", response_model=list[ParticipacionAerolinea])
async def obtener_participacion_aerolineas(
    db: Annotated[Session, Depends(get_db)],
    anio: int = Query(..., ge=2017),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Obtiene la participación de mercado de cada aerolínea en un año.

    Query params:
    - anio: Año (requerido)
    - limit: Número de aerolíneas a retornar (default 20)

    Returns:
        Lista de ParticipacionAerolinea ordenada por pasajeros totales
    """
    # Obtener todas las rutas del año
    rutas_anio = db.query(Ruta).filter(Ruta.anio == anio).all()

    if not rutas_anio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron datos para el año {anio}",
        )

    # Total de pasajeros en el año
    total_pasajeros = sum(r.pasajeros for r in rutas_anio)

    # Agregación por aerolínea
    aerolineas_data = {}
    for ruta in rutas_anio:
        for ruta_aero in ruta.rutas_aerolinea:
            aero = ruta_aero.aerolinea
            if aero not in aerolineas_data:
                aerolineas_data[aero] = {
                    "pasajeros": 0,
                    "vuelos": 0,
                    "factors": [],
                }
            aerolineas_data[aero]["pasajeros"] += ruta_aero.pasajeros
            aerolineas_data[aero]["vuelos"] += ruta_aero.vuelos
            aerolineas_data[aero]["factors"].append(ruta_aero.factor_ocupacion)

    # Construir response
    participaciones = [
        ParticipacionAerolinea(
            aerolinea=aero,
            pasajeros_total=data["pasajeros"],
            vuelos_total=data["vuelos"],
            factor_ocupacion_promedio=(
                sum(data["factors"]) / len(data["factors"])
                if data["factors"]
                else 0
            ),
            porcentaje_mercado=(
                (data["pasajeros"] / total_pasajeros * 100)
                if total_pasajeros > 0
                else 0
            ),
        )
        for aero, data in aerolineas_data.items()
    ]

    # Ordenar por pasajeros y limitar
    participaciones = sorted(
        participaciones,
        key=lambda x: x.pasajeros_total,
        reverse=True,
    )[:limit]

    return participaciones
