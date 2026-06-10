"""Tests de las reglas de limpieza (una por regla del brief)."""

import pandas as pd
import pytest

from src import config, limpieza


def test_esquema_valido_no_falla(construir, fila):
    limpieza.validar_esquema(construir(fila()))


def test_esquema_falta_columna_frena(construir, fila):
    df = construir(fila()).drop(columns=[config.COL_PASAJEROS])
    with pytest.raises(limpieza.EsquemaInvalido):
        limpieza.validar_esquema(df)


def test_regla1_fecha_fuera_de_rango(construir, fila):
    df = construir(fila(), fila(indice_tiempo="2015-01-01"))
    limpio, _ = limpieza.limpiar(df)
    assert len(limpio) == 1


def test_regla3_vuelo_no_comercial(construir, fila):
    df = construir(fila(), fila(aerolinea="0"), fila(aerolinea=None))
    limpio, _ = limpieza.limpiar(df)
    assert len(limpio) == 1


def test_regla4_solo_regular(construir, fila):
    df = construir(fila(), fila(clase_vuelo="No Regular"))
    limpio, _ = limpieza.limpiar(df)
    assert len(limpio) == 1
    assert (limpio[config.COL_CLASE] == config.VALOR_CLASE_REGULAR).all()


def test_regla6_pasajeros_negativos(construir, fila):
    df = construir(fila(), fila(pasajeros="-5"))
    limpio, _ = limpieza.limpiar(df)
    assert len(limpio) == 1


def test_pasajeros_cero_con_asientos_se_conserva(construir, fila):
    df = construir(fila(pasajeros="0", asientos="100"))
    limpio, _ = limpieza.limpiar(df)
    assert len(limpio) == 1
    assert limpio[config.COL_FACTOR].iloc[0] == 0.0


def test_regla5_asientos_cero_factor_nan(construir, fila):
    df = construir(fila(asientos="0"))
    limpio, _ = limpieza.limpiar(df)
    assert len(limpio) == 1
    assert pd.isna(limpio[config.COL_FACTOR].iloc[0])


def test_regla7_factor_imposible(construir, fila):
    df = construir(fila(), fila(pasajeros="120", asientos="100"))  # factor 1.2 > 1.05
    limpio, _ = limpieza.limpiar(df)
    assert len(limpio) == 1


def test_regla8_ruta_incompleta(construir, fila):
    df = construir(fila(), fila(destino_localidad=None))
    limpio, _ = limpieza.limpiar(df)
    assert len(limpio) == 1


def test_regla2_normalizacion_unifica_ruta(construir, fila):
    df = construir(
        fila(origen_localidad="buenos aires"),
        fila(origen_localidad="BUENOS AIRES "),
        fila(origen_localidad="Buenos Aires"),
    )
    limpio, _ = limpieza.limpiar(df)
    assert limpio[config.COL_RUTA].nunique() == 1
    assert limpio[config.COL_RUTA].iloc[0] == "Buenos Aires - Bariloche"


def test_regla9_direccionalidad_rutas_distintas(construir, fila):
    df = construir(
        fila(origen_localidad="buenos aires", destino_localidad="bariloche"),
        fila(origen_localidad="bariloche", destino_localidad="buenos aires"),
    )
    limpio, _ = limpieza.limpiar(df)
    assert limpio[config.COL_RUTA].nunique() == 2


def test_reporte_contabiliza_descartes(construir, fila):
    df = construir(fila(), fila(clase_vuelo="No Regular"))
    _, rep = limpieza.limpiar(df)
    paso4 = next(p for p in rep.pasos if p.regla == 4)
    assert paso4.descartadas == 1
