"""
Router de predicciones de demanda e inteligencia artificial.

Endpoints:
- POST /api/prediccion/demanda - Estimar pasajeros y nivel de demanda
- POST /api/prediccion/ocupacion - Estimar ocupación de ruta
- GET /api/prediccion/modelo/metricas - Obtener métricas de calidad del modelo
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import PrediccionRequest, DemandaResponse, OcupacionResponse, ModelMetricasResponse
from src.ia.predict import predictor

router = APIRouter()


@router.post("/prediccion/demanda", response_model=DemandaResponse, status_code=status.HTTP_200_OK)
async def predecir_demanda(
    payload: PrediccionRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Predice la cantidad de pasajeros esperados y clasifica el nivel de demanda
    (Alta, Media, Baja) para una ruta y periodo específicos.
    """
    try:
        res = predictor.predict(
            db=db,
            origen_localidad=payload.origen_localidad,
            destino_localidad=payload.destino_localidad,
            anio=payload.anio,
            mes=payload.mes,
            clasificacion_vuelo=payload.clasificacion_vuelo,
            asientos=payload.asientos,
            vuelos=payload.vuelos
        )
        return DemandaResponse(
            ruta=res["ruta"],
            pasajeros_predichos=res["pasajeros_predichos"],
            nivel_demanda=res["nivel_demanda"],
            alerta=res["alerta"],
            recomendacion=res["recomendacion"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la prediccion: {str(e)}"
        )


@router.post("/prediccion/ocupacion", response_model=OcupacionResponse, status_code=status.HTTP_200_OK)
async def predecir_ocupacion(
    payload: PrediccionRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Predice la cantidad de pasajeros esperados y estima la ocupación porcentual
    (con alertas y recomendaciones) para una ruta y periodo específicos.
    """
    try:
        res = predictor.predict(
            db=db,
            origen_localidad=payload.origen_localidad,
            destino_localidad=payload.destino_localidad,
            anio=payload.anio,
            mes=payload.mes,
            clasificacion_vuelo=payload.clasificacion_vuelo,
            asientos=payload.asientos,
            vuelos=payload.vuelos
        )
        return OcupacionResponse(
            ruta=res["ruta"],
            pasajeros_predichos=res["pasajeros_predichos"],
            asientos=res["asientos"],
            ocupacion_predicha=res["ocupacion_predicha"],
            nivel_ocupacion=res["nivel_ocupacion"],
            alerta=res["alerta"],
            recomendacion=res["recomendacion"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la prediccion: {str(e)}"
        )


@router.get("/modelo/metricas", response_model=ModelMetricasResponse, status_code=status.HTTP_200_OK)
async def obtener_metricas_modelo():
    """
    Devuelve los metadatos técnicos y las métricas de rendimiento (MAE, RMSE, R2, MAPE)
    del modelo de Inteligencia Artificial activo en el sistema.
    """
    if predictor.metadata is None:
        # Intentar recargar
        predictor._load_model()
        if predictor.metadata is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Metadatos y metricas del modelo no disponibles. Asegurate de haber entrenado el modelo."
            )
    
    return ModelMetricasResponse(
        modelo=predictor.metadata["modelo"],
        variable_objetivo=predictor.metadata["variable_objetivo"],
        registros_entrenamiento=predictor.metadata["registros_entrenamiento"],
        registros_prueba=predictor.metadata["registros_prueba"],
        mae=predictor.metadata["mae"],
        rmse=predictor.metadata["rmse"],
        mape=predictor.metadata["mape"],
        r2=predictor.metadata["r2"],
        fecha_entrenamiento=predictor.metadata["fecha_entrenamiento"],
        variables_usadas=predictor.metadata["variables_usadas"],
        tiempo_entrenamiento_seg=predictor.metadata["tiempo_entrenamiento_seg"]
    )
