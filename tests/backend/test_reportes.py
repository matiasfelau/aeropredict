"""
Tests para endpoints de reportes.
"""

import pytest
from src.backend.models import Ruta, RutaAerolinea


@pytest.fixture
def rutas_variadas(db):
    """Fixture para crear rutas con diferentes ocupaciones."""
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
            pasajeros=800,
            asientos=1000,
            vuelos=20,
            factor_ocupacion=0.80,
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
            pasajeros=100,
            asientos=500,
            vuelos=5,
            factor_ocupacion=0.20,  # Baja ocupación
        ),
        Ruta(
            anio=2023,
            mes=10,
            ruta="Buenos Aires - Iguazú",
            clasificacion_vuelo="Regular",
            origen_localidad="Buenos Aires",
            origen_provincia="CABA",
            destino_localidad="Puerto Iguazú",
            destino_provincia="Misiones",
            pasajeros=950,
            asientos=1000,
            vuelos=25,
            factor_ocupacion=0.95,  # Alta ocupación
        ),
    ]
    db.add_all(rutas)
    db.commit()
    return rutas


def test_reportar_ocupacion(client, rutas_variadas):
    """Test: reporte de ocupación por período."""
    response = client.get("/api/reportes/ocupacion?anio=2023&mes=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_obtener_tendencias(client, db, rutas_variadas):
    """Test: obtener tendencias de una ruta."""
    # Agregar más meses
    for mes in range(9, 11):
        ruta = Ruta(
            anio=2023,
            mes=mes,
            ruta="Buenos Aires - Bariloche",
            clasificacion_vuelo="Regular",
            origen_localidad="Buenos Aires",
            origen_provincia="CABA",
            destino_localidad="Bariloche",
            destino_provincia="Rio Negro",
            pasajeros=750,
            asientos=1000,
            vuelos=20,
            factor_ocupacion=0.75 + (mes - 9) * 0.05,
        )
        db.add(ruta)
    db.commit()

    response = client.get(
        "/api/reportes/tendencias?ruta=Bariloche&meses=12"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_obtener_tendencias_ruta_no_existe(client):
    """Test: tendencias de ruta inexistente retorna 404."""
    response = client.get(
        "/api/reportes/tendencias?ruta=RutaInexistente&meses=12"
    )
    assert response.status_code == 404


def test_obtener_alertas(client, db, rutas_variadas):
    """Test: obtener alertas de ocupación."""
    response = client.get("/api/reportes/alertas")
    assert response.status_code == 200
    data = response.json()
    # Debe haber al menos una alerta (baja y alta ocupación)
    assert len(data) > 0
    # Verificar tipos
    tipos = [alerta["tipo"] for alerta in data]
    assert "baja" in tipos
    assert "elevada" in tipos


def test_top_rutas_por_mes(client, rutas_variadas):
    """Test: top rutas por mes."""
    response = client.get(
        "/api/reportes/top-rutas?periodo=mes&anio=2023&mes=10&limit=2"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2
    # Primero debe estar Iguazú (mayor pasajeros)
    assert data[0]["ruta"] == "Buenos Aires - Iguazú"


def test_top_rutas_por_anio(client, db, rutas_variadas):
    """Test: top rutas por año."""
    response = client.get(
        "/api/reportes/top-rutas?periodo=anio&anio=2023&limit=2"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2


def test_top_rutas_periodo_mes_sin_parametros(client):
    """Test: top rutas con período=mes pero sin anio/mes retorna 400."""
    response = client.get("/api/reportes/top-rutas?periodo=mes&limit=5")
    assert response.status_code == 400


def test_participacion_aerolineas(client, db, rutas_variadas):
    """Test: participación de aerolíneas."""
    # Agregar rutas por aerolínea
    ruta = rutas_variadas[0]
    aero1 = RutaAerolinea(
        ruta_id=ruta.id,
        aerolinea="LATAM",
        pasajeros=400,
        asientos=500,
        vuelos=10,
        factor_ocupacion=0.80,
    )
    aero2 = RutaAerolinea(
        ruta_id=ruta.id,
        aerolinea="Aerolineas",
        pasajeros=400,
        asientos=500,
        vuelos=10,
        factor_ocupacion=0.80,
    )
    db.add_all([aero1, aero2])
    db.commit()

    response = client.get("/api/reportes/aerolineas?anio=2023&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_participacion_aerolineas_sin_anio(client):
    """Test: participación sin año retorna 400."""
    response = client.get("/api/reportes/aerolineas?limit=10")
    assert response.status_code == 422  # Validación Pydantic
