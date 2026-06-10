"""Tests de la normalización de texto (clave para joins y rutas)."""

import pandas as pd

from src import texto


def test_title_case_baja_conectores():
    s = pd.Series(["ciudad de buenos aires", "san carlos de bariloche"])
    out = texto.normalizar_serie(s, modo="title")
    assert list(out) == ["Ciudad de Buenos Aires", "San Carlos de Bariloche"]


def test_normalizar_texto_escalar_trim_y_title():
    assert texto.normalizar_texto("  río  negro ") == "Río Negro"


def test_modo_lower_y_strip():
    assert list(texto.normalizar_serie(pd.Series(["Cabotaje"]), modo="lower")) == ["cabotaje"]
    assert list(texto.normalizar_serie(pd.Series([" LATAM "]), modo="strip")) == ["LATAM"]


def test_clave_normalizada_quita_acentos_y_colapsa():
    assert texto.clave_normalizada("Córdoba") == "cordoba"
    assert texto.clave_normalizada("  EL  Calafate ") == "el calafate"


def test_vacios_y_nulos_a_na():
    out = texto.normalizar_serie(pd.Series(["", "  ", None]), modo="title")
    assert out.isna().all()
