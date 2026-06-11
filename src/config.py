"""Configuración central del módulo de datos de AeroPredict.

Único lugar para: rutas del proyecto, URLs de descarga, nombres de columnas
esperados (sección 3 del brief) y los umbrales/niveles acordados con diseño
(sección 6). Backend y el equipo de IA consumen estas mismas constantes, así
que cualquier cambio de criterio se hace acá y en ningún otro lado.
"""

from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Rutas del proyecto
# --------------------------------------------------------------------------- #
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"


def asegurar_directorios() -> None:
    """Crea las carpetas de trabajo si no existen."""
    for carpeta in (RAW_DIR, PROCESSED_DIR, REPORTS_DIR):
        carpeta.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# Fuente de datos: Conectividad Aérea — Subsecretaría de Turismo (datos.yvera)
# --------------------------------------------------------------------------- #
URL_MICRODATOS = (
    "https://datos.yvera.gob.ar/dataset/"
    "c0e7bc3d-553c-405c-8b32-79282b28ffd5/resource/"
    "aab49234-28c9-48ab-a978-a83485139290/download/base_microdatos.csv"
)
URL_AEROPUERTOS = (
    "https://datos.yvera.gob.ar/dataset/"
    "c0e7bc3d-553c-405c-8b32-79282b28ffd5/resource/"
    "d406a6fa-c209-4b15-b648-6bcceb1d040c/download/aeropuertos.csv"
)

# Archivos crudos (gitignored)
ARCHIVO_MICRODATOS = RAW_DIR / "base_microdatos.csv"
ARCHIVO_AEROPUERTOS = RAW_DIR / "aeropuertos.csv"

# --------------------------------------------------------------------------- #
# Entregables (data/processed/ + reports/)
# --------------------------------------------------------------------------- #
SALIDA_BASE_DIARIA = PROCESSED_DIR / "base_limpia_diaria.parquet"          # 5.1
SALIDA_MENSUAL_RUTA = PROCESSED_DIR / "base_mensual_ruta.csv"              # 5.2
SALIDA_MENSUAL_RUTA_AEROLINEA = PROCESSED_DIR / "base_mensual_ruta_aerolinea.csv"  # 5.3
SALIDA_AEROPUERTOS = PROCESSED_DIR / "aeropuertos_limpio.csv"             # 5.4
SALIDA_REPORTE = REPORTS_DIR / "calidad_datos.md"                         # 5.5

# --------------------------------------------------------------------------- #
# Esquema esperado del archivo principal (sección 3 del brief)
# --------------------------------------------------------------------------- #
COL_FECHA = "indice_tiempo"
COL_CLASIFICACION = "clasificacion_vuelo"
COL_CLASE = "clase_vuelo"
COL_AEROLINEA = "aerolinea"
COL_ORIGEN_AEROPUERTO = "origen_aeropuerto"
COL_ORIGEN_LOCALIDAD = "origen_localidad"
COL_ORIGEN_PROVINCIA = "origen_provincia"
COL_ORIGEN_CONTINENTE = "origen_continente"
COL_DESTINO_AEROPUERTO = "destino_aeropuerto"
COL_DESTINO_LOCALIDAD = "destino_localidad"
COL_DESTINO_PROVINCIA = "destino_provincia"
COL_DESTINO_CONTINENTE = "destino_continente"
COL_PASAJEROS = "pasajeros"
COL_ASIENTOS = "asientos"
COL_VUELOS = "vuelos"

# Las 15 columnas que el portal DEBE traer. Si falta alguna, el pipeline frena.
COLUMNAS_ESPERADAS = [
    COL_FECHA,
    COL_CLASIFICACION,
    COL_CLASE,
    COL_AEROLINEA,
    COL_ORIGEN_AEROPUERTO,
    COL_ORIGEN_LOCALIDAD,
    COL_ORIGEN_PROVINCIA,
    COL_ORIGEN_CONTINENTE,
    COL_DESTINO_AEROPUERTO,
    COL_DESTINO_LOCALIDAD,
    COL_DESTINO_PROVINCIA,
    COL_DESTINO_CONTINENTE,
    COL_PASAJEROS,
    COL_ASIENTOS,
    COL_VUELOS,
]

# Grupos de normalización de texto (regla 2 de limpieza)
COLUMNAS_TITLE_CASE = [   # nombres "humanos" -> Title Case, claves de join
    COL_ORIGEN_LOCALIDAD,
    COL_ORIGEN_PROVINCIA,
    COL_DESTINO_LOCALIDAD,
    COL_DESTINO_PROVINCIA,
    COL_ORIGEN_AEROPUERTO,
    COL_DESTINO_AEROPUERTO,
    COL_ORIGEN_CONTINENTE,
    COL_DESTINO_CONTINENTE,
]
COLUMNAS_LOWER = [        # categóricas canónicas -> minúscula
    COL_CLASIFICACION,
    COL_CLASE,
]
COLUMNAS_STRIP = [        # solo trim/colapsar espacios (no tocar mayúsculas)
    COL_AEROLINEA,
]
COLUMNAS_NUMERICAS = [COL_PASAJEROS, COL_ASIENTOS, COL_VUELOS]

# Columnas derivadas (sección 3: 12 directas + 4 derivadas)
COL_ANIO = "anio"
COL_MES = "mes"
COL_RUTA = "ruta"
COL_FACTOR = "factor_ocupacion"

# --------------------------------------------------------------------------- #
# Reglas de validación / limpieza (sección 4)
# --------------------------------------------------------------------------- #
ANIO_MIN = 2017          # regla 1: descartar fechas anteriores
ANIO_MAX: int | None = None  # None => año actual en tiempo de ejecución

VALOR_CLASE_REGULAR = "regular"            # regla 4: dataset de modelado
# regla 3: aerolínea vacía/nula/"0" => vuelo no comercial (privado)
VALORES_AEROLINEA_NO_COMERCIAL = {"", "0", "0.0", "nan", "none", "null"}

FACTOR_MAX_VALIDO = 1.05  # regla 7 y criterio de aceptación: factor en [0, 1.05]

# --------------------------------------------------------------------------- #
# Niveles y umbrales (sección 6). Backend los usa para las alertas.
# --------------------------------------------------------------------------- #
UMBRAL_BAJA_OCUPACION = 0.60       # < 0.60 -> "baja ocupación / promoción"
UMBRAL_OCUPACION_ELEVADA = 0.85    # >= 0.85 -> "alta demanda / ocupación elevada"

# Nivel de demanda (alta/media/baja) por terciles de pasajeros DENTRO de cada
# ruta: pasajeros < p33 = baja; p33..p66 = media; >= p66 = alta.
DEMANDA_PERCENTIL_BAJO = 1 / 3
DEMANDA_PERCENTIL_ALTO = 2 / 3

# Ruta turística con crecimiento: var. interanual > +20% sostenida 3 meses.
CRECIMIENTO_TURISTICO_PCT = 0.20
CRECIMIENTO_MESES_SOSTENIDO = 3

# --------------------------------------------------------------------------- #
# Esquema esperado del archivo auxiliar de aeropuertos (5.4)
# Mapa columna_origen -> columna_salida. CONFIRMAR los nombres reales en el EDA
# (Día 1) y ajustar acá si el CSV trae otros encabezados.
# --------------------------------------------------------------------------- #
AEROPUERTOS_MAPA_COLUMNAS = {
    "aeropuerto": "codigo",                    # código OACI (matchea origen_oaci/destino_oaci de la base)
    "aeropuerto_etiqueta_anac": "nombre",
    "localidad_etiqueta_indec": "localidad",
    "provincia_etiqueta_indec": "provincia",
    "pais_etiqueta_indec": "pais",
    "latitud": "latitud",
    "longitud": "longitud",
}
AEROPUERTOS_COLS_TITLE = ["nombre", "localidad", "provincia", "pais"]
AEROPUERTOS_COLS_NUM = ["latitud", "longitud"]
