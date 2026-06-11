"""Fixtures compartidas: builder de filas crudas sintéticas para los tests."""

import pandas as pd
import pytest

from src import config

# Fila válida base (vuelo regular, cabotaje). Los tests sobreescriben campos.
_BASE = dict(
    indice_tiempo="2023-01-05",
    clasificacion_vuelo="Cabotaje",
    clase_vuelo="Regular",
    aerolinea="Aerolineas Argentinas",
    origen_aeropuerto="AEP",
    origen_localidad="buenos aires",
    origen_provincia="Buenos Aires",
    origen_continente="América",
    destino_aeropuerto="BRC",
    destino_localidad="bariloche",
    destino_provincia="Rio Negro",
    destino_continente="América",
    pasajeros="80",
    asientos="100",
    vuelos="1",
)


@pytest.fixture
def fila():
    """Devuelve un builder: `fila(pasajeros="0")` -> dict de fila cruda."""
    def _fila(**over):
        f = dict(_BASE)
        f.update(over)
        return f
    return _fila


@pytest.fixture
def construir():
    """Arma un DataFrame crudo (dtype str) con las columnas esperadas."""
    def _construir(*filas):
        return pd.DataFrame(list(filas), columns=config.COLUMNAS_ESPERADAS).astype("string")
    return _construir
