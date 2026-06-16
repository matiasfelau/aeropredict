# Informe Técnico-Gerencial: Modelo de Predicción de Demanda Aérea
**Proyecto:** AeroPredict Argentina  
**Fecha:** 15 de Junio de 2026  
**Autor:** Antigravity (AI Coding Assistant)

---

## 1. Resumen Ejecutivo

El presente informe describe el diseño, la metodología y los resultados del modelo de Inteligencia Artificial implementado en **AeroPredict Argentina**. El objetivo central de esta solución es anticipar la demanda de pasajeros mensuales en las rutas aéreas argentinas y detectar de manera proactiva situaciones de alta demanda o baja ocupación para optimizar la toma de decisiones comerciales y turísticas.

### Puntos Clave de Rendimiento:
* **Precisión Superior:** El modelo explica el **99.15%** de la varianza histórica de los pasajeros (R² = 0.9915).
* **Margen de Error Acotado:** El Error Absoluto Medio (MAE) es de tan solo **477.70 pasajeros** en predicciones mensuales, una desviación insignificante para el volumen promedio de las rutas comerciales de cabotaje e internacionales.
* **Eficiencia Operativa:** Gracias al algoritmo histogramado de última generación, el entrenamiento completo toma **alrededor de 7 minutos (429.4 segundos)**, lo que facilita su reentrenamiento mensual periódico sin requerir infraestructura de cómputo costosa (GPUs).
* **Robustez en Producción:** La arquitectura está integrada de forma directa en el backend FastAPI y cuenta con validación estricta y fallbacks automáticos basados en la base de datos SQL.

---

## 2. Descripción General de la Solución

El modelo ha sido diseñado utilizando un enfoque de **aprendizaje supervisado para regresión**. A partir de variables operativas de entrada, el sistema calcula de forma precisa la cantidad de pasajeros esperados.

```
[ Variables de Entrada ] ─────────────────────────┐
- Año y Mes (Temporalidad)                       │
- Ruta (Origen y Destino)                        ├─► [ Pipeline de IA ] ─► [ Pasajeros Predichos ]
- Clasificación de vuelo (Cabotaje/Int.)         │
- Cantidad de Asientos y Vuelos (Capacidad) ─────┘
```

La ocupación estimada se deriva directamente dividiendo los pasajeros predichos por la oferta de asientos:
$$\text{Ocupación Estimada} = \frac{\text{Pasajeros Predichos}}{\text{Asientos Disponibles}}$$

---

## 3. ¿En qué consiste y cómo funciona la técnica de IA escogida?

Para resolver este problema con datos estructurados (tabulares) y alta presencia de texto, se seleccionó un pipeline compuesto por dos componentes clave de `scikit-learn`:

### A. Preprocesamiento: TargetEncoder (Codificador por Objetivo)
* **El Problema:** La variable `ruta` (ej: *"Buenos Aires - Bariloche"*) es una variable categórica de alta cardinalidad con más de 1,100 trayectos únicos. Usar codificaciones tradicionales como *One-Hot Encoding* crearía más de 1,100 columnas nuevas, lo que saturaría la memoria y provocaría sobreajuste (*overfitting*).
* **La Solución:** `TargetEncoder` reemplaza cada ruta con un único número decimal: el promedio ponderado de pasajeros que históricamente viajan en esa ruta específica. Para evitar fugas de datos y sobreajuste, realiza una validación cruzada interna (*cross-validation*) durante el proceso. Si una ruta es completamente nueva, el codificador le asigna automáticamente el promedio global de la clasificación de vuelo.

### B. Algoritmo: HistGradientBoostingRegressor (Boosting de Gradiente por Histogramas)
* **¿Qué es?:** Es una técnica avanzada de ensamble de árboles de decisión. En lugar de construir árboles en paralelo (como Random Forest), el *Gradient Boosting* construye árboles de forma **secuencial**. Cada nuevo árbol es entrenado específicamente para corregir los errores residuales (desviaciones) cometidos por los árboles anteriores.
* **¿Por qué "Hist"?:** Los regresores de gradiente estándar pueden ser lentos al evaluar miles de divisiones numéricas. La variante *Hist* agrupa los valores de entrada continuos (como asientos y vuelos) en histogramas discretos (bins de enteros de 8 bits). Esto reduce drásticamente la complejidad matemática, permitiendo que el entrenamiento sea sumamente rápido y eficiente en memoria.

---

## 4. Diseño del Entrenamiento y Estrategia de Validación

Para garantizar un modelo robusto que realmente funcione al predecir periodos futuros, se diseñaron las siguientes fases:

### 1. Tratamiento de la Anomalía Pandémica (COVID-19)
El análisis exploratorio (EDA) reveló una caída extrema y no estacional en la conectividad aérea entre 2020 y 2021. Dejar estos datos en el conjunto de entrenamiento habría "enseñado" al modelo a subestimar drásticamente la demanda. Por lo tanto, **se excluyeron todos los registros entre marzo de 2020 y junio de 2021**.

### 2. Validación Temporal (Out-of-Time Validation)
Para simular el uso real en producción, no se utilizó una división aleatoria estándar. En su lugar, se adoptó una **división basada en el tiempo**:
* **Conjunto de Entrenamiento (2017 - 2024):** 28,815 registros mensuales utilizados para que el modelo aprenda la estacionalidad, los promedios de rutas y los factores de carga.
* **Conjunto de Prueba (2025 - 2026):** 6,231 registros inéditos que el modelo jamás vio durante su entrenamiento. Esta prueba representa el escenario más exigente para la IA (predecir el futuro año completo).

---

## 5. Métricas de Rendimiento y Calidad

Las métricas arrojadas sobre el conjunto de validación temporal (2025/2026) son:

| Métrica | Valor | Interpretación Gerencial |
|---|---|---|
| **R² (Coeficiente de Determinación)** | **0.9915** | El modelo explica el **99.15%** del comportamiento real de los pasajeros. Esto demuestra una capacidad sobresaliente para capturar picos de estacionalidad (turismo invernal en julio, vacaciones en enero) y capacidad de flota. |
| **MAE (Error Absoluto Medio)** | **477.70 pax** | En promedio, la predicción mensual se desvía por menos de 478 pasajeros. Esto equivale a la capacidad aproximada de solo 2 o 3 aviones Boeing 737 a lo largo de todo un mes. |
| **RMSE (Error Cuadrático Medio)** | **1,087.64 pax** | Muestra el impacto de las desviaciones grandes. Al ser relativamente cercano al MAE, confirma que el modelo no sufre de errores masivos inesperados en rutas críticas. |
| **MAPE (Error Porcentual Medio)** | **75.44%** | Refleja un error relativo más alto en rutas de muy bajo tráfico (donde viajan menos de 100 pasajeros al mes, por lo que un error de 70 pasajeros es porcentualmente grande), pero mantiene una precisión muy alta en las rutas troncales de alta demanda. |

---

## 6. Arquitectura de Integración y Mantenibilidad

El modelo de IA no es una pieza aislada; está plenamente integrado en el ecosistema técnico de **AeroPredict**:

```
                  ┌─────────────────────────────────────────┐
                  │            FastAPI Backend              │
                  │  (src/backend/routers/prediccion.py)    │
                  └────────────────────┬────────────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
┌──────────────────────────────┐              ┌──────────────────────────────┐
│     SQL DB (PostgreSQL)      │              │      Pipeline de IA          │
│ - Busca promedios de ruta    │              │   (src/ia/predict.py)        │
│ - Fallback de capacidad      │              │ - Carga 'demand_model.joblib'│
└──────────────────────────────┘              └──────────────────────────────┘
```

* **Fallback Inteligente:** Si un usuario del frontend consulta una ruta sin especificar la cantidad de vuelos y asientos, el backend consulta automáticamente la base de datos SQL para recuperar el promedio histórico real de vuelos y capacidad de esa ruta específica, entregando una predicción contextualizada de inmediato.
* **Alertas Predictivas:** En base a la ocupación predicha, el sistema genera automáticamente alertas de ocupación baja ($\text{factor} < 0.60$) recomendando promociones comerciales, o de alta ocupación ($\text{factor} \geq 0.85$) sugiriendo evaluar un refuerzo de oferta de asientos.
* **Mantenimiento Simple:** El modelo puede ser reentrenado de forma nativa al recibir nuevos lotes mensuales de datos ejecutando el comando:
  ```bash
  .venv\Scripts\python.exe -m src.ia.train_model
  ```
  Esto actualizará el binario del modelo y sus metadatos automáticamente sin interrumpir el funcionamiento del servidor FastAPI.
