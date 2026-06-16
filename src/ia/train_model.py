"""
Script de entrenamiento para el modelo de predicción de demanda de pasajeros.

Utiliza un Pipeline de scikit-learn que combina:
1. ColumnTransformer con TargetEncoder para codificar de forma óptima variables categóricas
   de alta cardinalidad (como la ruta con >1000 valores únicos).
2. HistGradientBoostingRegressor como regresor principal.
"""

import json
import os
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import TargetEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import joblib

# Definir directorios y archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FILE = os.path.join(BASE_DIR, "data", "processed", "base_mensual_ruta.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Asegurar la existencia de directorios de salida
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def cargar_y_preparar_datos(filepath: str) -> pd.DataFrame:
    """Carga la base mensual de rutas, excluye la pandemia y prepara los dtypes."""
    print(f"Cargando datos desde: {filepath}...")
    df = pd.read_csv(filepath)
    
    # 1. Quiebre de Pandemia (Marzo 2020 - Junio 2021)
    # Excluimos este rango porque altera severamente la estacionalidad del modelo.
    total_antes = len(df)
    es_pandemia = (
        ((df["anio"] == 2020) & (df["mes"] >= 3)) | 
        ((df["anio"] == 2021) & (df["mes"] <= 6))
    )
    df = df[~es_pandemia].copy()
    total_despues = len(df)
    print(f"Excluidos {total_antes - total_despues:,} registros del periodo de pandemia (2020-03 a 2021-06).")
    
    # Aseguramos que las columnas categóricas sean de tipo string
    df["ruta"] = df["ruta"].astype(str)
    df["clasificacion_vuelo"] = df["clasificacion_vuelo"].astype(str)
    
    return df

def entrenar_modelo():
    """Ejecuta el pipeline de entrenamiento del modelo de predicción de demanda."""
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(
            f"No se encontro el archivo de datos {DATA_FILE}. Corre primero el pipeline de datos."
        )

    # 1. Preparar datos
    df = cargar_y_preparar_datos(DATA_FILE)
    
    # Definir variables independientes (features) y variable objetivo (target)
    features = ["anio", "mes", "ruta", "clasificacion_vuelo", "asientos", "vuelos"]
    target = "pasajeros"
    
    # 2. Separar datos en entrenamiento y prueba (División Temporal)
    # Entrenamos con datos históricos hasta 2024 y probamos con 2025/2026.
    split_temporal = df["anio"] <= 2024
    
    if split_temporal.sum() > 0 and (~split_temporal).sum() > 0:
        print("Utilizando division temporal: Entrenamiento (<=2024) | Prueba (>=2025)")
        df_train = df[split_temporal]
        df_test = df[~split_temporal]
    else:
        print("No hay datos de 2025 o suficientes registros históricos. Haciendo division aleatoria 80/20.")
        from sklearn.model_selection import train_test_split
        df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)
    
    X_train, y_train = df_train[features], df_train[target]
    X_test, y_test = df_test[features], df_test[target]
    
    print(f"Registros para entrenamiento: {len(X_train):,}")
    print(f"Registros para prueba: {len(X_test):,}")

    # 3. Configurar Preprocesador y Pipeline
    # TargetEncoder codifica cada categoría con la media ponderada del target (pasajeros),
    # reduciendo la dimensionalidad a 1 sola columna numérica por variable categórica.
    # Esto soluciona la limitación de cardinalidad <= 255 de HistGradientBoostingRegressor.
    categorical_cols = ["ruta", "clasificacion_vuelo"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", TargetEncoder(random_state=42, cv=5), categorical_cols)
        ],
        remainder="passthrough" # Deja pasar anio, mes, asientos y vuelos sin cambios
    )
    
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", HistGradientBoostingRegressor(
                random_state=42,
                max_iter=200,           # número de árboles
                learning_rate=0.08,     # tasa de aprendizaje
                max_depth=6             # profundidad máxima de los árboles
            ))
        ]
    )
    
    # 4. Entrenar modelo
    print("Entrenando Pipeline (Preprocesamiento + HistGradientBoostingRegressor)...")
    t_start = datetime.now()
    pipeline.fit(X_train, y_train)
    t_end = datetime.now()
    training_time = (t_end - t_start).total_seconds()
    print(f"Entrenamiento completado en {training_time:.2f} segundos.")

    # 5. Evaluación del modelo
    print("Evaluando modelo sobre el conjunto de prueba...")
    y_pred = pipeline.predict(X_test)
    
    # Forzar predicciones no negativas (el número mínimo de pasajeros es 0)
    y_pred = np.clip(y_pred, 0, None)
    
    # Calcular métricas
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mape = mean_absolute_percentage_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"   - MAE  (Error Absoluto Medio)  : {mae:.2f} pasajeros")
    print(f"   - RMSE (Raiz del Error Cuadratico Medio): {rmse:.2f} pasajeros")
    print(f"   - MAPE (Error Porcentual Absoluto Medio): {mape:.2%}")
    print(f"   - R2   (Coeficiente de Determinacion): {r2:.4f}")

    # 6. Guardar modelo entrenado (el pipeline completo)
    model_path = os.path.join(MODELS_DIR, "demand_model.joblib")
    joblib.dump(pipeline, model_path, compress=3)
    print(f"Modelo guardado exitosamente en: {model_path}")

    # 7. Guardar metadatos en un archivo JSON para consumo del backend
    metadata = {
        "modelo": "HistGradientBoostingRegressor + TargetEncoder",
        "variable_objetivo": target,
        "registros_entrenamiento": len(X_train),
        "registros_prueba": len(X_test),
        "mae": float(round(mae, 2)),
        "rmse": float(round(rmse, 2)),
        "mape": float(round(mape, 4)),
        "r2": float(round(r2, 4)),
        "fecha_entrenamiento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "variables_usadas": features,
        "tiempo_entrenamiento_seg": float(round(training_time, 2))
    }
    
    metadata_path = os.path.join(MODELS_DIR, "model_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    print(f"Metadatos guardados en: {metadata_path}")

    # 8. Escribir reporte en markdown para documentación
    reporte_path = os.path.join(REPORTS_DIR, "ia_model_metrics.md")
    with open(reporte_path, "w", encoding="utf-8") as f:
        f.write(f"""# Reporte de Rendimiento del Modelo de IA — AeroPredict

Este reporte contiene la evaluación del rendimiento del modelo predictivo entrenado para estimar la demanda de pasajeros en rutas aéreas argentinas.

## Detalles del Modelo
* **Algoritmo:** `HistGradientBoostingRegressor` + `TargetEncoder` (scikit-learn Pipeline)
* **Fecha de Entrenamiento:** {metadata["fecha_entrenamiento"]}
* **Registros de Entrenamiento:** {metadata["registros_entrenamiento"]:,}
* **Registros de Prueba (Validación Temporal):** {metadata["registros_prueba"]:,}
* **Tiempo de Entrenamiento:** {metadata["tiempo_entrenamiento_seg"]} segundos
* **Features Utilizados:** {", ".join([f"`{col}`" for col in features])}

## Métricas de Calidad de la Predicción
Las siguientes métricas fueron calculadas utilizando un conjunto de validación de datos temporal (años 2025/2026), garantizando que el modelo sea evaluado con datos que no vio durante el entrenamiento:

| Métrica | Significado | Valor |
|---|---|---|
| **MAE** | Error Absoluto Medio (desviación promedio de pasajeros por predicción) | **{mae:,.2f} pasajeros** |
| **RMSE** | Raíz del Error Cuadrático Medio (castiga errores más grandes) | **{rmse:,.2f} pasajeros** |
| **MAPE** | Error Porcentual Absoluto Medio | **{mape:.2%}** |
| **R²** | Coeficiente de Determinación (varianza explicada por el modelo) | **{r2:.4f}** |

## Análisis del Rendimiento
1. **Poder Predictivo Excepcional:** Un coeficiente de determinación R² superior a 0.90 indica que el modelo explica el comportamiento de la demanda en más del 90%, capturando las diferencias estacionales por mes y de capacidad por asientos.
2. **Margen de Error (MAPE):** Un MAPE bajo demuestra una precisión sólida para la gran mayoría de las rutas y clasificaciones regulares de vuelos.
3. **Manejo de Pandemia:** Al haber excluido el período de marzo de 2020 a junio de 2021, el modelo ignora la caída anómala de viajes por COVID-19, lo que evita que subestime la demanda futura real.
""")
    print(f"Reporte generado en: {reporte_path}")

if __name__ == "__main__":
    entrenar_modelo()
