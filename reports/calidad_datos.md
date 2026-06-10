# Reporte de calidad de datos — AeroPredict

> Generado automáticamente por `python -m src.pipeline`.

## Resumen

- Filas iniciales (CSV crudo): **1,048,043**
- Filas finales (base diaria limpia): **1,026,877**
- Filas descartadas en total: **21,166**
- Rango de fechas: **2017-01-01 → 2026-04-30**
- Rutas únicas: **1,343**
- Aerolíneas únicas: **47**
- Aeropuertos únicos: **266**

## Filas descartadas por regla

| Regla | Descripción | Antes | Después | Descartadas | Notas |
|---|---|---:|---:|---:|---|
| 1 | fecha inválida o fuera de rango | 1,048,043 | 1,048,043 | 0 | rango válido 2017-2026 |
| 2 | normalización de texto | 1,048,043 | 1,048,043 | 0 | transforma, no descarta |
| 3 | vuelos no comerciales | 1,048,043 | 1,048,043 | 0 |  |
| 4 | clase_vuelo != regular | 1,048,043 | 1,026,877 | 21,166 | decisión: el dataset de modelado usa solo vuelos regulares |
| 6 | pasajeros negativos/nulos | 1,026,877 | 1,026,877 | 0 | pasajeros=0 con asientos>0 se conserva (vuelo vacío) |
| 7 | factor_ocupacion > 1.05 | 1,026,877 | 1,026,877 | 0 |  |
| 8 | rutas incompletas (sin origen/destino) | 1,026,877 | 1,026,877 | 0 |  |

## Notas de calidad

- Vuelos no comerciales (aerolínea vacía/0) excluidos: 0
- Filas con asientos<=0 (factor diario NaN): 0
- Filas con factor_ocupacion>1.05 (sospechosas, excluidas del modelado): 0

## % de nulos por columna (base diaria limpia)

| Columna | % nulos |
|---|---:|
| `indice_tiempo` | 0.00% |
| `clasificacion_vuelo` | 0.00% |
| `clase_vuelo` | 0.00% |
| `aerolinea` | 0.00% |
| `origen_oaci` | 0.00% |
| `origen_aeropuerto` | 0.00% |
| `origen_localidad` | 0.00% |
| `origen_provincia` | 21.49% |
| `origen_pais` | 0.00% |
| `origen_continente` | 0.00% |
| `destino_oaci` | 0.00% |
| `destino_aeropuerto` | 0.00% |
| `destino_localidad` | 0.00% |
| `destino_provincia` | 21.58% |
| `destino_pais` | 0.00% |
| `destino_continente` | 0.00% |
| `pasajeros` | 0.00% |
| `asientos` | 0.00% |
| `vuelos` | 0.00% |
| `factor_ocupacion` | 0.00% |
| `ruta` | 0.00% |
| `anio` | 0.00% |
| `mes` | 0.00% |
