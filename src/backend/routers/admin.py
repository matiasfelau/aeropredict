"""
Router de administración.

Endpoints:
- POST /admin/reload-data — recarga datos desde CSVs del pipeline
- GET /admin/last-sync — metadata del último sync
"""

from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..dependencies import get_current_usuario
from ..database import get_db
from ..models import Usuario, ReporteCalidad, Ruta, Aeropuerto
from ..schemas import DataLoadResponse, SyncMetadataResponse, ReporteCalidadResponse
from ..loaders.load_data import cargar_datos_desde_pipeline

router = APIRouter()


@router.post("/reload-data", response_model=DataLoadResponse)
async def reload_data(
    db: Annotated[Session, Depends(get_db)],
    current_usuario: Annotated[Usuario, Depends(get_current_usuario)],
):
    """
    Recarga los datos desde los CSVs generados por el pipeline ETL.

    Requiere autenticación JWT.

    Returns:
        DataLoadResponse con estadísticas de la carga
    """
    try:
        resultado = cargar_datos_desde_pipeline(db)

        return DataLoadResponse(
            exitoso=True,
            timestamp=datetime.utcnow(),
            rutas_nuevas=resultado["rutas_nuevas"],
            rutas_actualizadas=resultado["rutas_actualizadas"],
            aeropuertos_nuevos=resultado["aeropuertos_nuevos"],
            aeropuertos_actualizados=resultado["aeropuertos_actualizados"],
            errores=resultado.get("errores", []),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cargar datos: {str(e)}",
        )


@router.get("/last-sync", response_model=SyncMetadataResponse)
async def obtener_sync_metadata(
    db: Annotated[Session, Depends(get_db)],
    current_usuario: Annotated[Usuario, Depends(get_current_usuario)],
):
    """
    Obtiene metadata del último sync con el pipeline ETL.

    Incluye:
    - Timestamp del último sync
    - Total de rutas y aeropuertos en DB
    - Reporte de calidad más reciente

    Requiere autenticación JWT.

    Returns:
        SyncMetadataResponse con metadata de sync
    """
    # Obtener último reporte de calidad
    ultimo_reporte = (
        db.query(ReporteCalidad)
        .order_by(desc(ReporteCalidad.fecha_generacion))
        .first()
    )

    # Contar rutas y aeropuertos
    total_rutas = db.query(Ruta).count()
    total_aeropuertos = db.query(Aeropuerto).count()

    return SyncMetadataResponse(
        ultimo_sync=ultimo_reporte.fecha_generacion if ultimo_reporte else None,
        rutas_totales=total_rutas,
        aeropuertos_totales=total_aeropuertos,
        reporte_calidad_mas_reciente=(
            ReporteCalidadResponse.model_validate(ultimo_reporte)
            if ultimo_reporte
            else None
        ),
    )
