"""
Tests para endpoints de predicción (IA).
"""

import pytest
from src.backend.models import Ruta


@pytest.fixture
def rutas_historicas(db):
    """Fixture para crear datos históricos en la DB que el predictor use como defaults."""
    rutas = [
        Ruta(
            anio=2023,
            mes=10,
            ruta="Buenos Aires - Bariloche",
            clasificacion_vuelo="cabotaje",
            origen_localidad="Buenos Aires",
            origen_provincia="CABA",
            destino_localidad="Bariloche",
            destino_provincia="Rio Negro",
            pasajeros=8000,
            asientos=10000,
            vuelos=50,
            factor_ocupacion=0.80,
        ),
        Ruta(
            anio=2024,
            mes=10,
            ruta="Buenos Aires - Bariloche",
            clasificacion_vuelo="cabotaje",
            origen_localidad="Buenos Aires",
            origen_provincia="CABA",
            destino_localidad="Bariloche",
            destino_provincia="Rio Negro",
            pasajeros=9000,
            asientos=10000,
            vuelos=50,
            factor_ocupacion=0.90,
        ),
    ]
    db.add_all(rutas)
    db.commit()
    return rutas


def test_predecir_demanda(client, db):
    """Test: predecir cantidad de pasajeros (demanda)."""
    payload = {
        "origen_localidad": "Buenos Aires",
        "destino_localidad": "Bariloche",
        "anio": 2025,
        "mes": 7,
        "clasificacion_vuelo": "cabotaje",
        "asientos": 10000,
        "vuelos": 50
    }
    response = client.post("/api/prediccion/demanda", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "ruta" in data
    assert data["ruta"] == "Buenos Aires - Bariloche"
    assert "pasajeros_predichos" in data
    assert isinstance(data["pasajeros_predichos"], int)
    assert "nivel_demanda" in data
    assert data["nivel_demanda"] in ["Baja", "Media", "Alta"]
    assert "alerta" in data
    assert "recomendacion" in data


def test_predecir_ocupacion(client, db):
    """Test: predecir factor de ocupación de vuelo."""
    payload = {
        "origen_localidad": "Buenos Aires",
        "destino_localidad": "Bariloche",
        "anio": 2025,
        "mes": 7,
        "clasificacion_vuelo": "cabotaje",
        "asientos": 10000,
        "vuelos": 50
    }
    response = client.post("/api/prediccion/ocupacion", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ruta"] == "Buenos Aires - Bariloche"
    assert isinstance(data["pasajeros_predichos"], int)
    assert data["asientos"] == 10000
    assert "ocupacion_predicha" in data
    assert 0.0 <= data["ocupacion_predicha"] <= 1.05
    assert data["nivel_ocupacion"] in ["Baja", "Media", "Alta"]
    assert "alerta" in data
    assert "recomendacion" in data


def test_predecir_demanda_valores_por_defecto(client, db, rutas_historicas):
    """Test: predicción utilizando promedios históricos cuando no se envían asientos/vuelos."""
    payload = {
        "origen_localidad": "Buenos Aires",
        "destino_localidad": "Bariloche",
        "anio": 2025,
        "mes": 7,
        "clasificacion_vuelo": "cabotaje"
        # asientos y vuelos omitidos
    }
    response = client.post("/api/prediccion/ocupacion", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Debe haber tomado el promedio histórico (asientos=10000, vuelos=50) de la ruta fixtures
    assert data["asientos"] == 10000


def test_obtener_metricas_modelo(client):
    """Test: obtener métricas de calidad y entrenamiento del modelo predictivo."""
    response = client.get("/api/modelo/metricas")
    assert response.status_code == 200
    data = response.json()
    assert "modelo" in data
    assert "mae" in data
    assert "rmse" in data
    assert "r2" in data
    assert "mape" in data
    assert isinstance(data["variables_usadas"], list)


def test_predecir_demanda_validation_errors(client):
    """Test: validar que inputs incorrectos retornen 422."""
    # Clasificación inválida
    payload_invalid_class = {
        "origen_localidad": "Buenos Aires",
        "destino_localidad": "Bariloche",
        "anio": 2025,
        "mes": 7,
        "clasificacion_vuelo": "charter"  # Inválido, solo cabotaje/internacional
    }
    response = client.post("/api/prediccion/demanda", json=payload_invalid_class)
    assert response.status_code == 422

    # Mes inválido
    payload_invalid_month = {
        "origen_localidad": "Buenos Aires",
        "destino_localidad": "Bariloche",
        "anio": 2025,
        "mes": 13,  # Inválido
        "clasificacion_vuelo": "cabotaje"
    }
    response = client.post("/api/prediccion/demanda", json=payload_invalid_month)
    assert response.status_code == 422
