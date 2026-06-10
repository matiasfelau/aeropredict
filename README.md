# AeroPredict Argentina — Módulo de DATOS

Pipeline que toma la base de Conectividad Aérea (datos.yvera.gob.ar), la limpia
y entrega bases listas para que **backend responda todos los endpoints sin
transformaciones adicionales** y para entrenar el **modelo de predicción**.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (PowerShell)
pip install -r requirements.txt
```

## Correr el pipeline

```bash
python -m src.descarga        # baja los CSV de origen a data/raw/ (una vez, cientos de MB)
python -m src.pipeline        # limpia + agrega + reporte (descarga si falta)
python -m src.pipeline --no-descarga   # si ya bajaste los datos
```

Salidas en `data/processed/` y `reports/`.

## Estructura

```
src/
├── config.py       # URLs, nombres de columnas, umbrales (única fuente de verdad)
├── texto.py        # normalización compartida (joins base <-> aeropuertos)
├── descarga.py     # descarga con caché local
├── limpieza.py     # reglas 1–10 + acumulación de stats de calidad
├── agregacion.py   # bases mensuales (5.2/5.3) + aeropuertos (5.4)
├── reporte.py      # reports/calidad_datos.md (regla 11)
└── pipeline.py     # python -m src.pipeline corre todo
```

## Entregables

| Archivo | Qué es |
|---|---|
| `data/processed/base_limpia_diaria.parquet` | Base diaria limpia + `anio`, `mes`, `ruta`, `factor_ocupacion`. |
| `data/processed/base_mensual_ruta.csv` | **Principal.** Una fila por (anio, mes, ruta, clasificación). Base de endpoints + tabla de entrenamiento. |
| `data/processed/base_mensual_ruta_aerolinea.csv` | Igual + aerolínea en la clave (opcional). |
| `data/processed/aeropuertos_limpio.csv` | Aeropuertos geolocalizados, normalizados con el mismo criterio de texto. |
| `reports/calidad_datos.md` | Reporte de calidad (filas descartadas por regla, nulos, rangos, conteos). |

## Contrato de datos (entregables → endpoints de backend)

| Endpoint | Se resuelve con |
|---|---|
| `GET /api/resumen` | agregación total de `base_mensual_ruta.csv` |
| `GET /api/evolucion-pasajeros` | group by anio+mes sobre `base_mensual_ruta.csv` |
| `GET /api/rutas/top?limite=N` | `base_mensual_ruta.csv` ordenada por pasajeros |
| `GET /api/rutas/ocupacion` | `base_mensual_ruta.csv` (factor ya calculado) |
| `GET /api/rutas/baja-ocupacion?umbral=0.60` | `base_mensual_ruta.csv` + umbral |
| `GET /api/alertas` | `base_mensual_ruta.csv` + reglas de umbrales |
| `POST /api/prediccion/*` | modelo entrenado sobre `base_mensual_ruta.csv` |
| `GET /api/aeropuertos` | `aeropuertos_limpio.csv` |

## Umbrales (en `src/config.py`)

- Baja ocupación: `factor_ocupacion < 0.60`
- Ocupación elevada: `factor_ocupacion >= 0.85`
- Nivel de demanda: terciles de pasajeros mensuales **dentro de cada ruta**.
- Ruta turística con crecimiento: var. interanual > +20% sostenida 3 meses.

## Decisiones clave

- `factor_ocupacion` mensual = `suma(pasajeros) / suma(asientos)` sobre totales del mes (no promedio de factores diarios).
- Direccionalidad: "A - B" ≠ "B - A" (rutas distintas).
- `ruta` se construye **después** de normalizar texto.
- Dataset de modelado: solo `clase_vuelo = regular`.
- Quiebre 2020–2021 (pandemia): tratarlo aparte en el modelo (ver nota para IA).

## Hallazgos del EDA (Día 1, confirmado contra los datos reales)

Datos: **1.048.043 filas**, rango **2017-01-01 → 2026-04-30**.

- **Esquema:** están las 15 columnas esperadas + 4 extra útiles que el brief no listaba: `origen_oaci`, `destino_oaci`, `origen_pais`, `destino_pais`.
- **Calidad altísima:** las reglas 1, 3, 5, 6, 7 y 8 descartan **0 filas** (no hay fechas inválidas, aerolíneas vacías, asientos≤0, pasajeros negativos ni factor>1.05 — el máximo es 1.0). Solo la **regla 4** filtra 21.166 vuelos no-regulares.
- **Join 5.2 ↔ 5.4 por localidad:** cierra con 0 mismatches para los 49 aeropuertos argentinos (criterio de aceptación #5 ✅). Además la base trae **código OACI** que matchea 100% con `aeropuertos.csv` → join alternativo más robusto disponible si backend lo prefiere.
- **`San Fernando` (SADF)** aparece en 5.4 pero no en 5.2: sus únicos 8 vuelos son no-regulares → los filtra la regla 4. Pérdida explicable, no inesperada.
- **`provincia` ~21% nula:** son rutas internacionales (localidades extranjeras sin provincia argentina). Esperado; no es columna clave.
- Variantes de texto: la fuente ya viene consistente; `src/texto.ALIASES` quedó vacío (se completa si aparecen variantes en futuras actualizaciones mensuales).

## Salida del último run

| Entregable | Filas |
|---|---|
| `base_limpia_diaria.parquet` | 1.026.877 |
| `base_mensual_ruta.csv` | 37.402 |
| `base_mensual_ruta_aerolinea.csv` | 58.201 |
| `aeropuertos_limpio.csv` | 49 |

Control de suma: pasajeros diario = mensual = **224.770.277** (diferencia 0).
