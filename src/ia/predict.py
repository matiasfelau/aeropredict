"""
Clase predictora para el modelo de demanda de AeroPredict.

Carga el pipeline guardado (TargetEncoder + HistGradientBoostingRegressor)
y realiza predicciones de pasajeros y factor de ocupación con reglas de negocio.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.backend.models import Ruta

# Definir la ruta del modelo y metadatos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "models" / "demand_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"

class DemandPredictor:
    """Clase para cargar el modelo de regresión y realizar predicciones."""

    def __init__(self):
        self.model = None
        self.metadata = None
        self._load_model()

    def _load_model(self):
        """Carga el modelo joblib y su archivo de metadatos asociado."""
        # 1. Descargar de Hugging Face si no existe localmente
        if not MODEL_PATH.exists() or not METADATA_PATH.exists():
            print("El modelo o metadatos no existen localmente. Intentando descargar de Hugging Face...")
            try:
                from huggingface_hub import hf_hub_download
                from src.backend.config import settings
                import shutil
                
                os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
                
                if not MODEL_PATH.exists():
                    descargado_model = hf_hub_download(
                        repo_id=settings.HF_MODEL_REPO_ID,
                        filename="demand_model.joblib"
                    )
                    shutil.copy(descargado_model, MODEL_PATH)
                    print(f"Modelo descargado de Hugging Face y guardado en {MODEL_PATH}")
                
                if not METADATA_PATH.exists():
                    descargado_meta = hf_hub_download(
                        repo_id=settings.HF_MODEL_REPO_ID,
                        filename="model_metadata.json"
                    )
                    shutil.copy(descargado_meta, METADATA_PATH)
                    print(f"Metadatos descargados de Hugging Face y guardados en {METADATA_PATH}")
            except Exception as e:
                print(f"No se pudo descargar el modelo de Hugging Face: {e}. Se intentara usar el archivo local.")

        # 2. Cargar archivo local
        if MODEL_PATH.exists():
            try:
                self.model = joblib.load(MODEL_PATH)
                print(f"Modelo cargado exitosamente desde {MODEL_PATH}")
            except Exception as e:
                print(f"Error al cargar el modelo joblib: {e}")
        else:
            print(f"Advertencia: El archivo del modelo no existe en {MODEL_PATH}")

        if METADATA_PATH.exists():
            try:
                with open(METADATA_PATH, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                print("Metadatos del modelo cargados exitosamente.")
            except Exception as e:
                print(f"Error al cargar los metadatos del modelo: {e}")

    def predict(
        self,
        db: Session,
        origen_localidad: str,
        destino_localidad: str,
        anio: int,
        mes: int,
        clasificacion_vuelo: str,
        asientos: Optional[int] = None,
        vuelos: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Realiza la predicción de pasajeros y calcula el factor de ocupación estimado.
        
        Si no se especifican asientos o vuelos, busca promedios históricos en la base de datos.
        """
        if self.model is None:
            # Reintentar cargar el modelo si no estaba cargado
            self._load_model()
            if self.model is None:
                raise ValueError("El modelo de prediccion no esta cargado.")

        ruta = f"{origen_localidad} - {destino_localidad}"

        # 1. Obtener valores por defecto si no son provistos por el usuario
        if asientos is None or vuelos is None:
            # Consultar promedios históricos en la base de datos para esta ruta y tipo de vuelo
            result = db.query(
                func.avg(Ruta.asientos),
                func.avg(Ruta.vuelos)
            ).filter(
                Ruta.ruta == ruta,
                Ruta.clasificacion_vuelo == clasificacion_vuelo
            ).first()

            hist_asientos, hist_vuelos = result if result else (None, None)

            if asientos is None:
                asientos = int(round(hist_asientos)) if hist_asientos is not None else 3000
            if vuelos is None:
                vuelos = int(round(hist_vuelos)) if hist_vuelos is not None else 20

        # 2. Formatear la entrada para el pipeline
        # Debe contener exactamente las columnas usadas en el entrenamiento
        input_data = pd.DataFrame([{
            "anio": anio,
            "mes": mes,
            "ruta": ruta,
            "clasificacion_vuelo": clasificacion_vuelo,
            "asientos": asientos,
            "vuelos": vuelos
        }])

        # 3. Realizar predicción
        pred_pax = self.model.predict(input_data)[0]
        # Impedir predicciones negativas de pasajeros
        pred_pax = max(0, int(round(pred_pax)))

        # 4. Calcular factor de ocupación estimado
        factor_ocupacion = pred_pax / asientos if asientos > 0 else 0.0
        # Imponer el límite superior de 1.05 conforme al negocio
        factor_ocupacion = min(1.05, factor_ocupacion)

        # 5. Determinar el nivel de demanda y ocupación
        # Obtenemos los pasajeros históricos de la ruta para calcular los percentiles terciles (33.3% y 66.7%)
        hist_pax_list = [
            r[0] for r in db.query(Ruta.pasajeros).filter(
                Ruta.ruta == ruta,
                Ruta.clasificacion_vuelo == clasificacion_vuelo
            ).all()
        ]

        if len(hist_pax_list) >= 5:
            # Criterio percentil local
            p33 = np.percentile(hist_pax_list, 33.3)
            p67 = np.percentile(hist_pax_list, 66.7)
        else:
            # Fallback: percentil general de la misma clasificacion_vuelo
            gen_pax_list = [
                r[0] for r in db.query(Ruta.pasajeros).filter(
                    Ruta.clasificacion_vuelo == clasificacion_vuelo
                ).all()
            ]
            if len(gen_pax_list) >= 10:
                p33 = np.percentile(gen_pax_list, 33.3)
                p67 = np.percentile(gen_pax_list, 66.7)
            else:
                p33 = 1000.0
                p67 = 5000.0

        if pred_pax < p33:
            nivel_demanda = "Baja"
        elif pred_pax < p67:
            nivel_demanda = "Media"
        else:
            nivel_demanda = "Alta"

        # Nivel de ocupación y recomendaciones basadas en umbrales de config.py
        if factor_ocupacion < 0.60:
            nivel_ocupacion = "Baja"
            alerta = "Baja ocupacion"
            recomendacion = "Evaluar promociones o revisar frecuencia de vuelos."
        elif factor_ocupacion < 0.85:
            nivel_ocupacion = "Media"
            alerta = "Ocupacion normal"
            recomendacion = "Mantener frecuencias actuales y monitorear evolucion."
        else:
            nivel_ocupacion = "Alta"
            alerta = "Alta demanda esperada"
            recomendacion = "Monitorear disponibilidad o evaluar refuerzo de oferta de asientos."

        return {
            "ruta": ruta,
            "pasajeros_predichos": pred_pax,
            "asientos": asientos,
            "vuelos": vuelos,
            "ocupacion_predicha": float(round(factor_ocupacion, 4)),
            "nivel_demanda": nivel_demanda,
            "nivel_ocupacion": nivel_ocupacion,
            "alerta": alerta,
            "recomendacion": recomendacion
        }

# Instancia global para ser importada en el backend
predictor = DemandPredictor()
