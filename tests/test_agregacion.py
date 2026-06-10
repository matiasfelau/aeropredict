"""Tests de la agregación mensual (5.2) y limpieza de aeropuertos (5.4)."""

import pandas as pd

from src import agregacion, config, limpieza


def test_factor_mensual_sobre_totales(construir, fila):
    # Dos vuelos misma ruta/mes: factor = (80+60)/(100+100) = 0.7, NO promedio de diarios.
    df = construir(
        fila(indice_tiempo="2023-01-05", pasajeros="80", asientos="100"),
        fila(indice_tiempo="2023-01-20", pasajeros="60", asientos="100"),
    )
    limpio, _ = limpieza.limpiar(df)
    m = agregacion.agregar_mensual_ruta(limpio)
    assert len(m) == 1
    assert m[config.COL_FACTOR].iloc[0] == 0.7


def test_5_2_sin_nulos_clave_y_factor_en_rango(construir, fila):
    df = construir(
        fila(),
        fila(clasificacion_vuelo="Internacional", destino_localidad="madrid",
             destino_provincia=None, pasajeros="200", asientos="250"),
    )
    limpio, _ = limpieza.limpiar(df)
    m = agregacion.agregar_mensual_ruta(limpio)
    clave = [config.COL_ANIO, config.COL_MES, config.COL_RUTA, config.COL_CLASIFICACION,
             "pasajeros", "asientos", "vuelos", config.COL_FACTOR]
    assert m[clave].isna().sum().sum() == 0
    assert m[config.COL_FACTOR].between(0, config.FACTOR_MAX_VALIDO).all()


def test_conteos_mensuales_son_enteros(construir, fila):
    limpio, _ = limpieza.limpiar(construir(fila()))
    m = agregacion.agregar_mensual_ruta(limpio)
    for col in ("pasajeros", "asientos", "vuelos"):
        assert m[col].dtype.kind == "i"


def test_aeropuertos_normaliza_y_mapea_columnas():
    crudo = pd.DataFrame({
        "aeropuerto": ["sabe"],
        "aeropuerto_etiqueta_anac": ["aeroparque jorge newbery"],
        "localidad_etiqueta_indec": ["ciudad de buenos aires"],
        "provincia_etiqueta_indec": ["buenos aires"],
        "pais_etiqueta_indec": ["argentina"],
        "latitud": ["-34.55"],
        "longitud": ["-58.41"],
    })
    a = agregacion.limpiar_aeropuertos(crudo)
    assert {"codigo", "nombre", "localidad", "provincia", "pais", "latitud", "longitud"} <= set(a.columns)
    r = a.iloc[0]
    assert r["codigo"] == "SABE"                          # OACI en mayúscula
    assert r["localidad"] == "Ciudad de Buenos Aires"     # Title Case + conector
    assert r["latitud"] == -34.55                          # numérico
