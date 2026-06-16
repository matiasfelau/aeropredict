"""
Tests para endpoints de rutas.
"""

import pytest
from src.backend.models import Ruta


@pytest.fixture
def rutas_test(db):
    """Fixture para crear rutas de test."""
    rutas = [
        Ruta(
            anio=2023,
            mes=10,
            ruta="Buenos Aires - Bariloche",
            clasificacion_vuelo="Regular",
            origen_localidad="Buenos Aires",
            origen_provincia="CABA",
            destino_localidad="Bariloche",
            destino_provincia="Rio Negro",
            pasajeros=500,
            asientos=600,
            vuelos=10,
            factor_ocupacion=0.83,
        ),
        Ruta(
            anio=2023,
            mes=10,
            ruta="Buenos Aires - Mendoza",
            clasificacion_vuelo="Regular",
            origen_localidad="Buenos Aires",
            origen_provincia="CABA",
            destino_localidad="Mendoza",
            destino_provincia="Mendoza",
            pasajeros=300,
            asientos=400,
            vuelos=8,
            factor_ocupacion=0.75,
        ),
    ]
    db.add_all(rutas)
    db.commit()
    return rutas


def test_listar_rutas(client, rutas_test):
    """Test: listar rutas con paginación."""
    response = client.get("/api/rutas?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["limit"] == 10
    assert len(data["items"]) == 2


def test_obtener_ruta_por_id(client, rutas_test):
    """Test: obtener detalle de ruta."""
    ruta_id = rutas_test[0].id
    response = client.get(f"/api/rutas/{ruta_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["ruta"] == "Buenos Aires - Bariloche"
    assert data["anio"] == 2023
    assert data["mes"] == 10


def test_obtener_ruta_no_existe(client):
    """Test: obtener ruta inexistente retorna 404."""
    response = client.get("/api/rutas/99999")
    assert response.status_code == 404


def test_buscar_rutas_por_anio_mes(client, rutas_test):
    """Test: búsqueda avanzada por año y mes."""
    response = client.get("/api/rutas/buscar/avanzada?anio=2023&mes=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


def test_buscar_rutas_por_origen(client, rutas_test):
    """Test: búsqueda avanzada por origen."""
    response = client.get("/api/rutas/buscar/avanzada?origen_localidad=Buenos%20Aires")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


def test_buscar_rutas_por_factor_ocupacion(client, rutas_test):
    """Test: búsqueda avanzada por rango de factor de ocupación."""
    response = client.get("/api/rutas/buscar/avanzada?factor_min=0.80&factor_max=0.85")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["ruta"] == "Buenos Aires - Bariloche"


def test_buscar_por_nombre_ruta(client, rutas_test):
    """Test: búsqueda por nombre de ruta."""
    response = client.get("/api/rutas/ruta/Bariloche")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["ruta"] == "Buenos Aires - Bariloche"
