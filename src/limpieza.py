"""Limpieza del archivo principal (reglas 1–10 de la sección 4 del brief).

Cada regla que descarta filas se contabiliza para el reporte de calidad
(regla 11). El orden importa: la columna `ruta` se construye DESPUÉS de la
normalización de texto, y `factor_ocupacion` después de limpiar los numéricos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

from . import config, texto


class EsquemaInvalido(Exception):
    """El CSV de origen no tiene las columnas esperadas (sección 3)."""


# --------------------------------------------------------------------------- #
# Acumulador de estadísticas para el reporte de calidad
# --------------------------------------------------------------------------- #
@dataclass
class PasoLimpieza:
    regla: int
    nombre: str
    filas_antes: int
    filas_despues: int
    notas: str = ""

    @property
    def descartadas(self) -> int:
        return self.filas_antes - self.filas_despues


@dataclass
class ReporteCalidad:
    filas_iniciales: int = 0
    filas_finales: int = 0
    pasos: list[PasoLimpieza] = field(default_factory=list)
    rango_fechas: tuple = (None, None)
    nulos_por_columna: dict = field(default_factory=dict)
    n_rutas: int = 0
    n_aerolineas: int = 0
    n_aeropuertos: int = 0
    notas_extra: list[str] = field(default_factory=list)

    def registrar(self, regla, nombre, antes, despues, notas=""):
        paso = PasoLimpieza(regla, nombre, antes, despues, notas)
        self.pasos.append(paso)
        if paso.descartadas:
            print(f"[limpieza] regla {regla} ({nombre}): "
                  f"-{paso.descartadas:,} filas ({antes:,} -> {despues:,})")
        return despues


# --------------------------------------------------------------------------- #
# Carga + validación de esquema
# --------------------------------------------------------------------------- #
def cargar_microdatos(path=None, nrows=None) -> pd.DataFrame:
    """Lee el CSV crudo como texto (dtype=str) para coercionar después con
    control total. `nrows` sirve para muestrear en el EDA."""
    path = path or config.ARCHIVO_MICRODATOS
    if not path.exists():
        raise FileNotFoundError(
            f"No está {path}. Corré primero: python -m src.descarga"
        )
    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=True,
        na_values=["", "NA", "NaN", "null", "NULL"],
        nrows=nrows,
    )


def validar_esquema(df: pd.DataFrame) -> None:
    """Frena el pipeline si el portal cambió los nombres de columna."""
    faltan = [c for c in config.COLUMNAS_ESPERADAS if c not in df.columns]
    if faltan:
        raise EsquemaInvalido(
            f"Faltan columnas esperadas: {faltan}. "
            f"Presentes: {list(df.columns)}. "
            "El portal pudo cambiar el esquema: frenar y avisar a backend/diseño."
        )


# --------------------------------------------------------------------------- #
# Pipeline de limpieza
# --------------------------------------------------------------------------- #
def limpiar(df: pd.DataFrame) -> tuple[pd.DataFrame, ReporteCalidad]:
    """Aplica las reglas 1–10 en orden y devuelve (base_diaria_limpia, reporte)."""
    rep = ReporteCalidad(filas_iniciales=len(df))
    df = df.copy()

    # --- Regla 1: parseo de fecha + rango razonable -----------------------
    df[config.COL_FECHA] = pd.to_datetime(
        df[config.COL_FECHA], errors="coerce", format="ISO8601"
    )
    antes = len(df)
    anio_max = config.ANIO_MAX or datetime.now().year
    fechas_ok = (
        df[config.COL_FECHA].notna()
        & (df[config.COL_FECHA].dt.year >= config.ANIO_MIN)
        & (df[config.COL_FECHA].dt.year <= anio_max)
    )
    df = df[fechas_ok]
    rep.registrar(1, "fecha inválida o fuera de rango", antes, len(df),
                  f"rango válido {config.ANIO_MIN}-{anio_max}")

    # --- Regla 2: normalización de texto (NO descarta filas) --------------
    for col in config.COLUMNAS_TITLE_CASE:
        df[col] = texto.normalizar_serie(df[col], modo="title")
    for col in config.COLUMNAS_LOWER:
        df[col] = texto.normalizar_serie(df[col], modo="lower")
    for col in config.COLUMNAS_STRIP:
        df[col] = texto.normalizar_serie(df[col], modo="strip")
    rep.registrar(2, "normalización de texto", len(df), len(df),
                  "transforma, no descarta")

    # --- Regla 3: vuelos no comerciales (aerolínea vacía/nula/"0") --------
    antes = len(df)
    clave_aero = df[config.COL_AEROLINEA].map(texto.clave_normalizada)
    es_no_comercial = (
        df[config.COL_AEROLINEA].isna()
        | clave_aero.isin(config.VALORES_AEROLINEA_NO_COMERCIAL)
    )
    rep.notas_extra.append(
        f"Vuelos no comerciales (aerolínea vacía/0) excluidos: "
        f"{int(es_no_comercial.sum()):,}"
    )
    df = df[~es_no_comercial]
    rep.registrar(3, "vuelos no comerciales", antes, len(df))

    # --- Regla 4: filtro de regularidad (solo 'regular' para modelado) ----
    antes = len(df)
    df = df[df[config.COL_CLASE] == config.VALOR_CLASE_REGULAR]
    rep.registrar(4, "clase_vuelo != regular", antes, len(df),
                  "decisión: el dataset de modelado usa solo vuelos regulares")

    # --- Coerción de numéricos (necesaria para reglas 5–7) ----------------
    for col in config.COLUMNAS_NUMERICAS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Regla 6: pasajeros negativos o no parseables ---------------------
    # (se aplica antes de calcular factor; pasajeros=0 con asientos>0 es válido)
    antes = len(df)
    pasajeros_ok = df[config.COL_PASAJEROS].notna() & (df[config.COL_PASAJEROS] >= 0)
    df = df[pasajeros_ok]
    rep.registrar(6, "pasajeros negativos/nulos", antes, len(df),
                  "pasajeros=0 con asientos>0 se conserva (vuelo vacío)")

    # --- Regla 5: asientos <= 0 quedan fuera del cálculo de factor --------
    # No se descarta la fila; el factor diario queda NaN (no dividir por cero).
    asientos = df[config.COL_ASIENTOS]
    asientos_validos = asientos.notna() & (asientos > 0)
    df[config.COL_FACTOR] = float("nan")
    df.loc[asientos_validos, config.COL_FACTOR] = (
        df.loc[asientos_validos, config.COL_PASAJEROS]
        / df.loc[asientos_validos, config.COL_ASIENTOS]
    )
    rep.notas_extra.append(
        f"Filas con asientos<=0 (factor diario NaN): "
        f"{int((~asientos_validos).sum()):,}"
    )

    # --- Regla 7: factores imposibles (> 1.05) -> sospechosos, fuera ------
    antes = len(df)
    factor = pd.to_numeric(df[config.COL_FACTOR], errors="coerce")
    sospechosos = factor > config.FACTOR_MAX_VALIDO
    rep.notas_extra.append(
        f"Filas con factor_ocupacion>{config.FACTOR_MAX_VALIDO} (sospechosas, "
        f"excluidas del modelado): {int(sospechosos.sum()):,}"
    )
    df = df[~sospechosos]
    rep.registrar(7, f"factor_ocupacion > {config.FACTOR_MAX_VALIDO}", antes, len(df))

    # --- Regla 8: rutas incompletas (sin origen o sin destino) ------------
    antes = len(df)
    completas = (
        df[config.COL_ORIGEN_LOCALIDAD].notna()
        & df[config.COL_DESTINO_LOCALIDAD].notna()
    )
    df = df[completas]
    rep.registrar(8, "rutas incompletas (sin origen/destino)", antes, len(df))

    # --- Regla 9: direccionalidad -> NO se unifica (no requiere acción) ---

    # --- Regla 10: columna `ruta` (después de normalizar texto) -----------
    df[config.COL_RUTA] = (
        df[config.COL_ORIGEN_LOCALIDAD] + " - " + df[config.COL_DESTINO_LOCALIDAD]
    )

    # --- Derivadas: anio, mes ---------------------------------------------
    df[config.COL_ANIO] = df[config.COL_FECHA].dt.year.astype("int64")
    df[config.COL_MES] = df[config.COL_FECHA].dt.month.astype("int64")

    # --- Métricas finales para el reporte ---------------------------------
    rep.filas_finales = len(df)
    if len(df):
        rep.rango_fechas = (
            df[config.COL_FECHA].min().date().isoformat(),
            df[config.COL_FECHA].max().date().isoformat(),
        )
    rep.nulos_por_columna = {
        col: round(float(df[col].isna().mean()) * 100, 2) for col in df.columns
    }
    rep.n_rutas = int(df[config.COL_RUTA].nunique())
    rep.n_aerolineas = int(df[config.COL_AEROLINEA].nunique())
    rep.n_aeropuertos = int(
        pd.concat([
            df[config.COL_ORIGEN_AEROPUERTO],
            df[config.COL_DESTINO_AEROPUERTO],
        ]).nunique()
    )

    return df, rep


if __name__ == "__main__":
    datos = cargar_microdatos()
    validar_esquema(datos)
    limpio, reporte = limpiar(datos)
    print(f"[limpieza] {reporte.filas_iniciales:,} -> {reporte.filas_finales:,} filas")
