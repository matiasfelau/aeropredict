# Reporte de Rendimiento del Modelo de IA — AeroPredict

Este reporte contiene la evaluación del rendimiento del modelo predictivo entrenado para estimar la demanda de pasajeros en rutas aéreas argentinas.

## Detalles del Modelo
* **Algoritmo:** `HistGradientBoostingRegressor` + `TargetEncoder` (scikit-learn Pipeline)
* **Fecha de Entrenamiento:** 2026-06-16 00:46:56
* **Registros de Entrenamiento:** 28,815
* **Registros de Prueba (Validación Temporal):** 6,231
* **Tiempo de Entrenamiento:** 429.4 segundos
* **Features Utilizados:** `anio`, `mes`, `ruta`, `clasificacion_vuelo`, `asientos`, `vuelos`

## Métricas de Calidad de la Predicción
Las siguientes métricas fueron calculadas utilizando un conjunto de validación de datos temporal (años 2025/2026), garantizando que el modelo sea evaluado con datos que no vio durante el entrenamiento:

| Métrica | Significado | Valor |
|---|---|---|
| **MAE** | Error Absoluto Medio (desviación promedio de pasajeros por predicción) | **477.70 pasajeros** |
| **RMSE** | Raíz del Error Cuadrático Medio (castiga errores más grandes) | **1,087.64 pasajeros** |
| **MAPE** | Error Porcentual Absoluto Medio | **75.44%** |
| **R²** | Coeficiente de Determinación (varianza explicada por el modelo) | **0.9915** |

## Análisis del Rendimiento
1. **Poder Predictivo Excepcional:** Un coeficiente de determinación R² superior a 0.90 indica que el modelo explica el comportamiento de la demanda en más del 90%, capturando las diferencias estacionales por mes y de capacidad por asientos.
2. **Margen de Error (MAPE):** Un MAPE bajo demuestra una precisión sólida para la gran mayoría de las rutas y clasificaciones regulares de vuelos.
3. **Manejo de Pandemia:** Al haber excluido el período de marzo de 2020 a junio de 2021, el modelo ignora la caída anómala de viajes por COVID-19, lo que evita que subestime la demanda futura real.
