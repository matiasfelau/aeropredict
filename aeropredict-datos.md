# AeroPredict Argentina — Módulo de DATOS

> Brief para Claude Code. Rol: equipo de DATOS. Plazo total del proyecto: 1 semana y media (~4 días para datos). Este módulo alimenta a backend (endpoints), al modelo de IA y al frontend.

## 1. Contexto del proyecto completo

AeroPredict Argentina predice demanda de pasajeros en rutas aéreas argentinas y detecta rutas con alta demanda o baja ocupación. El sistema tiene 5 módulos:

1. **Dashboard general:** totales de pasajeros, vuelos, asientos, factor de ocupación promedio y gráfico de evolución mensual de pasajeros.
2. **Análisis de rutas:** ranking de rutas por pasajeros, factor de ocupación por ruta, detección de baja ocupación, comparación cabotaje vs. internacional.
3. **Predicción de demanda (IA):** el usuario ingresa ruta, mes, año, clasificación del vuelo y opcionalmente asientos/vuelos; el sistema devuelve pasajeros estimados, ocupación estimada y nivel de demanda (alta / media / baja).
4. **Alertas inteligentes:** "alta demanda esperada", "baja ocupación" (umbral inicial: factor < 0.60), "posible necesidad de promoción", "ruta turística con crecimiento", "ocupación elevada".
5. **Mapa de aeropuertos (OPCIONAL):** aeropuertos geolocalizados con métricas asociadas.

**El módulo de datos debe entregar bases limpias que permitan responder TODOS los endpoints de backend sin transformaciones adicionales** (ver sección 7).

## 2. Fuente de datos

**Dataset:** Conectividad Aérea — Subsecretaría de Turismo (datos.yvera.gob.ar). Actualización mensual.

**Archivo principal (confirmado):** Base agregada de frecuencias aéreas (`base_microdatos.csv`). Datos a nivel **diario** de vuelos, pasajeros y asientos por origen, destino, aerolínea, clase y clasificación del vuelo.

- Descarga: `https://datos.yvera.gob.ar/dataset/c0e7bc3d-553c-405c-8b32-79282b28ffd5/resource/aab49234-28c9-48ab-a978-a83485139290/download/base_microdatos.csv`
- ADVERTENCIA: archivo grande (cientos de MB). Descargar una sola vez a `data/raw/` (gitignored). Leer con `pandas` con `dtype` explícitos; usar `chunksize` si hace falta. Intermedios en Parquet.

**Archivo auxiliar (para Módulo 5 y endpoint `/api/aeropuertos`):** aeropuertos geolocalizados (código, nombre, localidad, provincia, país, latitud, longitud):
`https://datos.yvera.gob.ar/dataset/c0e7bc3d-553c-405c-8b32-79282b28ffd5/resource/d406a6fa-c209-4b15-b648-6bcceb1d040c/download/aeropuertos.csv`

## 3. Esquema del archivo principal (verificado en la documentación oficial)

| Columna | Tipo | Descripción |
|---|---|---|
| `indice_tiempo` | fecha ISO-8601 | Índice de tiempo diario |
| `clasificacion_vuelo` | string | Tipo de conexión (cabotaje / internacional) |
| `clase_vuelo` | string | Regularidad de la ruta (regular / no regular) |
| `aerolinea` | string | Aerolínea comercial |
| `origen_aeropuerto` | string | Aeropuerto de origen |
| `origen_localidad` | string | Localidad de origen |
| `origen_provincia` | string | Provincia de origen |
| `origen_continente` | string | Continente de origen |
| `destino_aeropuerto` | string | Aeropuerto de destino |
| `destino_localidad` | string | Localidad de destino |
| `destino_provincia` | string | Provincia de destino |
| `destino_continente` | string | Continente de destino |
| `pasajeros` | number | Cantidad de pasajeros |
| `asientos` | number | Cantidad de asientos |
| `vuelos` | number | Cantidad de vuelos |

Validar al inicio del pipeline que estas columnas existan con estos nombres; si el portal cambió algo, frenar y reportar.

Las 16 variables pedidas por diseño están cubiertas: 12 directas + 4 derivadas (`anio`, `mes`, `ruta`, `factor_ocupacion`).

## 4. Reglas de limpieza (aplicar en este orden; documentar cuántas filas afecta cada una)

1. **Parseo de fecha:** convertir `indice_tiempo` a datetime. Descartar fechas inválidas o fuera de rango razonable (antes de 2017 o futuras) y reportarlas.
2. **Normalización de texto:** trim, Title Case en localidades/aeropuertos, unificar tildes y variantes del mismo nombre (clave: cualquier inconsistencia duplica rutas en los rankings). Listar valores únicos antes y después.
3. **Vuelos no comerciales:** filas con `aerolinea` vacía, nula o `"0"` (vuelos privados). Excluirlas del dataset principal y contabilizarlas.
4. **Filtro de regularidad:** para el dataset de modelado, quedarse con `clase_vuelo = regular`. Documentar la decisión.
5. **Asientos en cero:** nunca dividir por cero. Filas con `asientos <= 0` quedan fuera del cálculo de `factor_ocupacion`.
6. **Pasajeros:** descartar negativos. Pasajeros = 0 con asientos > 0 es válido (vuelo vacío), conservar.
7. **Factores imposibles:** filas con `factor_ocupacion > 1.05` se marcan como sospechosas, se excluyen del modelado y se reportan.
8. **Rutas incompletas:** descartar filas sin origen o sin destino.
9. **Direccionalidad:** "Buenos Aires - Bariloche" y "Bariloche - Buenos Aires" son **rutas distintas**. No unificar.
10. **Columna `ruta`:** `origen_localidad + " - " + destino_localidad`, construida DESPUÉS de la normalización de texto.
11. **Reporte de calidad:** generar `reports/calidad_datos.md` con: filas totales, filas descartadas por regla, % de nulos por columna, rango de fechas, cantidad de rutas/aerolíneas/aeropuertos únicos.

## 5. Entregables en `data/processed/`

### 5.1 `base_limpia_diaria.parquet`
Base diaria limpia: columnas originales normalizadas + `anio`, `mes`, `ruta`, `factor_ocupacion`.

### 5.2 `base_mensual_ruta.csv` — ENTREGABLE PRINCIPAL
Una fila por (`anio`, `mes`, `ruta`, `clasificacion_vuelo`):

| Columna | Tipo | Regla |
|---|---|---|
| `anio` | int | |
| `mes` | int | 1–12 |
| `ruta` | string | "Localidad Origen - Localidad Destino" |
| `clasificacion_vuelo` | string | cabotaje / internacional |
| `origen_localidad` | string | |
| `origen_provincia` | string | |
| `destino_localidad` | string | |
| `destino_provincia` | string | |
| `pasajeros` | int | suma del mes |
| `asientos` | int | suma del mes |
| `vuelos` | int | suma del mes |
| `factor_ocupacion` | float | `pasajeros / asientos` SOBRE LOS TOTALES mensuales (no promedio de factores diarios) |

Esta tabla es a la vez la base de los endpoints de consulta y la **tabla de entrenamiento del modelo** (target: `pasajeros`; features: ruta, mes, anio, clasificación, asientos, vuelos — coincide con el formulario de la pantalla de predicción).

### 5.3 `base_mensual_ruta_aerolinea.csv` (opcional)
Igual que 5.2 pero agregando `aerolinea` a la clave (la pantalla de predicción contempla aerolínea como input opcional, y habilita filtros por aerolínea).

### 5.4 `aeropuertos_limpio.csv`
Del archivo auxiliar: `codigo`, `nombre`, `localidad`, `provincia`, `pais`, `latitud`, `longitud`, normalizado con el MISMO criterio de texto que la base principal para que los joins por localidad funcionen. Alimenta `/api/aeropuertos` y el Módulo 5.

### 5.5 `reports/calidad_datos.md`
Reporte de calidad descrito en la regla 11.

## 6. Niveles y umbrales (acordados con diseño; backend los usa para alertas)

Definirlos como constantes configurables en un solo lugar (`src/config.py`):

- **Baja ocupación:** `factor_ocupacion < 0.60` → alerta "Baja ocupación / posible necesidad de promoción".
- **Ocupación elevada:** `factor_ocupacion >= 0.85` → alerta "Alta demanda esperada / ocupación elevada".
- **Nivel de demanda (alta/media/baja):** calcular por percentiles de pasajeros mensuales DENTRO de cada ruta (p.ej. tercil superior = alta) o contra el promedio histórico de la ruta. Documentar el criterio elegido para que el modelo y las alertas usen el mismo.
- **Ruta turística con crecimiento:** variación interanual de pasajeros > +20% sostenida en los últimos 3 meses con datos (criterio inicial, ajustable).

## 7. Mapeo entregables → endpoints de backend

| Endpoint | Se resuelve con |
|---|---|
| `GET /api/resumen` | agregación total de 5.2 |
| `GET /api/evolucion-pasajeros` (filtros anio, clasificación) | group by anio+mes sobre 5.2 |
| `GET /api/rutas/top?limite=N` | 5.2 ordenada por pasajeros |
| `GET /api/rutas/ocupacion` | 5.2 (factor ya calculado) |
| `GET /api/rutas/baja-ocupacion?umbral=0.60` | 5.2 + umbral de sección 6 |
| `GET /api/alertas` | 5.2 + reglas de sección 6 |
| `POST /api/prediccion/demanda` y `/ocupacion` | modelo entrenado sobre 5.2 |
| `GET /api/aeropuertos` | 5.4 |

Si backend puede cargar 5.2 y 5.4 tal cual y responder todos los GET, el contrato está cumplido.

## 8. Estructura sugerida del repo

```
aeropredict-datos/
├── data/
│   ├── raw/            # CSVs crudos (gitignored)
│   └── processed/      # entregables 5.1–5.4
├── notebooks/
│   └── 01_eda.ipynb
├── src/
│   ├── config.py       # URLs, umbrales, nombres de columnas
│   ├── descarga.py     # descarga con caché local
│   ├── limpieza.py     # reglas 1–10
│   ├── agregacion.py   # bases mensuales + aeropuertos
│   └── pipeline.py     # python -m src.pipeline corre todo
├── reports/
│   └── calidad_datos.md
├── requirements.txt    # pandas, pyarrow, requests, matplotlib
├── .gitignore
└── README.md
```

## 9. Plan de trabajo (~4 días)

1. **Día 1 — Descarga + EDA:** confirmar esquema real, rango de fechas, valores únicos, nulos, ceros, casos raros. Volcar hallazgos en el notebook. Avisar a diseño/backend si algo no coincide con este documento.
2. **Día 2 — Limpieza:** implementar reglas 1–10 + reporte de calidad.
3. **Día 3 — Agregación:** generar 5.1–5.4. Validar con sumas de control (total de pasajeros antes vs. después de agregar).
4. **Día 4 — Contrato y entrega:** README con el contrato de datos, umbrales de sección 6 confirmados con el equipo, entrega a backend.

## 10. Criterios de aceptación

- El pipeline corre de punta a punta con un solo comando.
- `base_mensual_ruta.csv` sin nulos en columnas clave y con `factor_ocupacion` en [0, 1.05].
- Toda fila descartada está contabilizada en el reporte de calidad.
- Backend responde los 6 endpoints GET principales usando solo 5.2 y 5.4, sin limpieza adicional.
- Las localidades de 5.2 matchean con las de 5.4 (join por localidad sin pérdidas inesperadas).

## 11. Notas para el modelo predictivo (equipo de IA)

- Granularidad recomendada: mensual por ruta (coincide con el formulario de la pantalla de predicción).
- La serie tiene un quiebre fuerte en 2020–2021 (pandemia): excluir del entrenamiento o tratar explícitamente.
- Estacionalidad anual marcada: `mes` es feature clave; considerar codificarlo cíclico o como categórico.
- Features sugeridos desde datos: lag de pasajeros del mismo mes del año anterior y promedio histórico de la ruta (se pueden agregar como columnas extra a 5.2 si el equipo de IA las pide).
