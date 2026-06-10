"""Agregación: de la base diaria limpia a los entregables 5.2, 5.3 y 5.4.

Clave del factor mensual (sección 5.2): se calcula como
suma(pasajeros) / suma(asientos) SOBRE LOS TOTALES del mes, NO como promedio
de los factores diarios.
"""

from __future__ import annotations

import pandas as pd

from . import config, texto


def _factor_sobre_totales(pasajeros: pd.Series, asientos: pd.Series) -> pd.Series:
    """factor = pasajeros/asientos sobre totales; NaN si asientos<=0."""
    factor = pd.Series(float("nan"), index=pasajeros.index, dtype="float64")
    validos = asientos > 0
    factor[validos] = (pasajeros[validos] / asientos[validos]).round(4)
    return factor


def agregar_mensual_ruta(df_diario: pd.DataFrame) -> pd.DataFrame:
    """Entregable 5.2: una fila por (anio, mes, ruta, clasificacion_vuelo)."""
    claves = [
        config.COL_ANIO,
        config.COL_MES,
        config.COL_RUTA,
        config.COL_CLASIFICACION,
    ]
    agg = (
        df_diario.groupby(claves, dropna=False, observed=True)
        .agg(
            origen_localidad=(config.COL_ORIGEN_LOCALIDAD, "first"),
            origen_provincia=(config.COL_ORIGEN_PROVINCIA, "first"),
            destino_localidad=(config.COL_DESTINO_LOCALIDAD, "first"),
            destino_provincia=(config.COL_DESTINO_PROVINCIA, "first"),
            pasajeros=(config.COL_PASAJEROS, "sum"),
            asientos=(config.COL_ASIENTOS, "sum"),
            vuelos=(config.COL_VUELOS, "sum"),
        )
        .reset_index()
    )

    agg[config.COL_FACTOR] = _factor_sobre_totales(agg["pasajeros"], agg["asientos"])

    # Criterio de aceptación: factor en [0, 1.05] y sin nulos en columnas clave.
    # Se descartan meses sin asientos (factor indefinido) o con factor imposible.
    antes = len(agg)
    agg = agg[agg[config.COL_FACTOR].notna() & (agg[config.COL_FACTOR] <= config.FACTOR_MAX_VALIDO)]
    descartados = antes - len(agg)
    if descartados:
        print(f"[agregacion] 5.2: -{descartados:,} filas mensuales "
              f"(factor NaN o > {config.FACTOR_MAX_VALIDO})")

    # Tipos: enteros en conteos, orden de columnas según la tabla 5.2.
    for col in ("pasajeros", "asientos", "vuelos"):
        agg[col] = agg[col].round().astype("int64")

    columnas = [
        config.COL_ANIO, config.COL_MES, config.COL_RUTA, config.COL_CLASIFICACION,
        "origen_localidad", "origen_provincia",
        "destino_localidad", "destino_provincia",
        "pasajeros", "asientos", "vuelos", config.COL_FACTOR,
    ]
    return (
        agg[columnas]
        .sort_values([config.COL_ANIO, config.COL_MES, config.COL_RUTA])
        .reset_index(drop=True)
    )


def agregar_mensual_ruta_aerolinea(df_diario: pd.DataFrame) -> pd.DataFrame:
    """Entregable 5.3 (opcional): igual que 5.2 + aerolínea en la clave."""
    claves = [
        config.COL_ANIO, config.COL_MES, config.COL_RUTA,
        config.COL_CLASIFICACION, config.COL_AEROLINEA,
    ]
    agg = (
        df_diario.groupby(claves, dropna=False, observed=True)
        .agg(
            origen_localidad=(config.COL_ORIGEN_LOCALIDAD, "first"),
            origen_provincia=(config.COL_ORIGEN_PROVINCIA, "first"),
            destino_localidad=(config.COL_DESTINO_LOCALIDAD, "first"),
            destino_provincia=(config.COL_DESTINO_PROVINCIA, "first"),
            pasajeros=(config.COL_PASAJEROS, "sum"),
            asientos=(config.COL_ASIENTOS, "sum"),
            vuelos=(config.COL_VUELOS, "sum"),
        )
        .reset_index()
    )
    agg[config.COL_FACTOR] = _factor_sobre_totales(agg["pasajeros"], agg["asientos"])
    agg = agg[agg[config.COL_FACTOR].notna() & (agg[config.COL_FACTOR] <= config.FACTOR_MAX_VALIDO)]
    for col in ("pasajeros", "asientos", "vuelos"):
        agg[col] = agg[col].round().astype("int64")

    columnas = [
        config.COL_ANIO, config.COL_MES, config.COL_RUTA, config.COL_CLASIFICACION,
        config.COL_AEROLINEA,
        "origen_localidad", "origen_provincia",
        "destino_localidad", "destino_provincia",
        "pasajeros", "asientos", "vuelos", config.COL_FACTOR,
    ]
    return (
        agg[columnas]
        .sort_values([config.COL_ANIO, config.COL_MES, config.COL_RUTA])
        .reset_index(drop=True)
    )


def limpiar_aeropuertos(df_aero: pd.DataFrame) -> pd.DataFrame:
    """Entregable 5.4: normaliza el archivo auxiliar con el MISMO criterio de
    texto que la base principal, para que los joins por localidad cierren.

    Ojo: los nombres de columna del CSV de aeropuertos se confirman en el EDA
    (config.AEROPUERTOS_MAPA_COLUMNAS). Acá se renombran y normalizan.
    """
    mapa = config.AEROPUERTOS_MAPA_COLUMNAS
    faltan = [orig for orig in mapa if orig not in df_aero.columns]
    if faltan:
        print(f"[agregacion] AVISO aeropuertos: columnas no encontradas {faltan}. "
              "Confirmá los encabezados reales en config.AEROPUERTOS_MAPA_COLUMNAS.")

    presentes = {orig: dest for orig, dest in mapa.items() if orig in df_aero.columns}
    df = df_aero[list(presentes)].rename(columns=presentes).copy()

    for col in config.AEROPUERTOS_COLS_TITLE:
        if col in df.columns:
            df[col] = texto.normalizar_serie(df[col], modo="title")
    if "codigo" in df.columns:
        df["codigo"] = df["codigo"].astype("string").str.strip().str.upper()
    for col in config.AEROPUERTOS_COLS_NUM:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.reset_index(drop=True)
