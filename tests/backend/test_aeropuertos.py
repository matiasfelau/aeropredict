"""
Tests para endpoints de aeropuertos.
"""

import pytest
from src.backend.models import Aeropuerto


@pytest.fixture
def aeropuertos_test(db):
    """Fixture para crear aeropuertos de test."""
    aeropuertos = [
        Aeropuerto(
            codigo_oaci="SABE",
            nombre="Ministro Pistarini",
            localidad="Buenos Aires",
            provincia="Buenos Aires",
            pais="Argentina",
            latitud=-34.8226,
            longitud=-58.5356,
        ),
        Aeropuerto(
            codigo_oaci="SAEZ",
            nombre="Aeroparque Jorge Newbery",
            localidad="Buenos Aires",
            provincia="Buenos Aires",
            pais="Argentina",
            latitud=-34.5623,
            longitud=-58.4161,
        ),
        Aeropuerto(
            codigo_oaci="SAZS",
            nombre="San Fernando",
            localidad="San Fernando",
            provincia="Buenos Aires",
            pais="Argentina",
            latitud=-34.4520,
            longitud=-58.4780,
        ),
    ]
    db.add_all(aeropuertos)
    db.commit()
    return aeropuertos


def test_listar_aeropuertos(client, aeropuertos_test):
    """Test: listar aeropuertos con paginación."""
    response = client.get("/api/aeropuertos?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_obtener_aeropuerto_por_codigo(client, aeropuertos_test):
    """Test: obtener detalle de aeropuerto."""
    response = client.get("/api/aeropuertos/SABE")
    assert response.status_code == 200
    data = response.json()
    assert data["codigo_oaci"] == "SABE"
    assert data["nombre"] == "Ministro Pistarini"
    assert data["localidad"] == "Buenos Aires"


def test_obtener_aeropuerto_codigo_minuscula(client, aeropuertos_test):
    """Test: obtener aeropuerto con código en minúscula."""
    response = client.get("/api/aeropuertos/sabe")
    assert response.status_code == 200
    data = response.json()
    assert data["codigo_oaci"] == "SABE"


def test_obtener_aeropuerto_no_existe(client):
    """Test: obtener aeropuerto inexistente retorna 404."""
    response = client.get("/api/aeropuertos/XXXX")
    assert response.status_code == 404


def test_buscar_aeropuertos_por_localidad(client, aeropuertos_test):
    """Test: búsqueda avanzada por localidad."""
    response = client.get("/api/aeropuertos/buscar/avanzada?localidad=Buenos%20Aires")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


def test_buscar_aeropuertos_por_nombre(client, aeropuertos_test):
    """Test: búsqueda avanzada por nombre."""
    response = client.get("/api/aeropuertos/buscar/avanzada?nombre=Newbery")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["codigo_oaci"] == "SAEZ"


def test_buscar_aeropuertos_por_provincia(client, aeropuertos_test):
    """Test: búsqueda avanzada por provincia."""
    response = client.get("/api/aeropuertos/buscar/avanzada?provincia=Buenos%20Aires")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
