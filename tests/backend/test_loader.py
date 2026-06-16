"""
Tests para data loader (integración con pipeline ETL).
"""

import pytest
import tempfile
from pathlib import Path
import pandas as pd
from src.backend.loaders.load_data import cargar_datos_desde_pipeline
from src.backend.models import Ruta, Aeropuerto


def test_cargar_datos_archivos_inexistentes(db, monkeypatch):
    """Test: cargar datos cuando CSVs no existen."""
    # Mock DATA_PROCESSED_PATH a directorio vacío
    with tempfile.TemporaryDirectory() as tmpdir:
        from src.backend.config import settings
        monkeypatch.setattr(settings, "DATA_PROCESSED_PATH", Path(tmpdir))

        resultado = cargar_datos_desde_pipeline(db)

        assert not resultado["exitoso"]
        assert len(resultado["errores"]) > 0


def test_cargar_rutas_csv(db, monkeypatch):
    """Test: cargar rutas desde CSV."""
    # Crear CSV temporal
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Crear CSV de rutas
        rutas_data = {
            "anio": [2023, 2023],
            "mes": [10, 10],
            "ruta": ["Buenos Aires - Bariloche", "Buenos Aires - Mendoza"],
            "clasificacion_vuelo": ["Regular", "Regular"],
            "origen_localidad": ["Buenos Aires", "Buenos Aires"],
            "origen_provincia": ["CABA", "CABA"],
            "destino_localidad": ["Bariloche", "Mendoza"],
            "destino_provincia": ["Rio Negro", "Mendoza"],
            "pasajeros": [500, 300],
            "asientos": [600, 400],
            "vuelos": [10, 8],
            "factor_ocupacion": [0.83, 0.75],
        }
        df_rutas = pd.DataFrame(rutas_data)
        df_rutas.to_csv(tmpdir_path / "base_mensual_ruta.csv", index=False)

        # Crear CSV de aeropuertos (vacío pero válido)
        aeropuertos_data = {
            "codigo": ["SABE", "SAEZ"],
            "nombre": ["Ministro Pistarini", "Aeroparque"],
            "localidad": ["Buenos Aires", "Buenos Aires"],
            "provincia": ["Buenos Aires", "Buenos Aires"],
            "pais": ["Argentina", "Argentina"],
            "latitud": [-34.8226, -34.5623],
            "longitud": [-58.5356, -58.4161],
        }
        df_aero = pd.DataFrame(aeropuertos_data)
        df_aero.to_csv(tmpdir_path / "aeropuertos_limpio.csv", index=False)

        # Mock settings
        from src.backend.config import settings
        monkeypatch.setattr(settings, "DATA_PROCESSED_PATH", tmpdir_path)

        # Cargar datos
        resultado = cargar_datos_desde_pipeline(db)

        # Validar
        assert resultado["exitoso"]
        assert resultado["rutas_nuevas"] == 2
        assert resultado["aeropuertos_nuevos"] == 2

        # Verificar en DB
        rutas_db = db.query(Ruta).all()
        assert len(rutas_db) == 2

        aeropuertos_db = db.query(Aeropuerto).all()
        assert len(aeropuertos_db) == 2


def test_cargar_datos_actualiza_existentes(db, monkeypatch):
    """Test: cargar datos actualiza registros existentes."""
    # Crear ruta inicial
    ruta_inicial = Ruta(
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
    )
    db.add(ruta_inicial)
    db.commit()

    # Crear CSV con datos actualizados
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        rutas_data = {
            "anio": [2023],
            "mes": [10],
            "ruta": ["Buenos Aires - Bariloche"],
            "clasificacion_vuelo": ["Regular"],
            "origen_localidad": ["Buenos Aires"],
            "origen_provincia": ["CABA"],
            "destino_localidad": ["Bariloche"],
            "destino_provincia": ["Rio Negro"],
            "pasajeros": [600],  # Cambio
            "asientos": [700],  # Cambio
            "vuelos": [12],  # Cambio
            "factor_ocupacion": [0.86],  # Cambio
        }
        df_rutas = pd.DataFrame(rutas_data)
        df_rutas.to_csv(tmpdir_path / "base_mensual_ruta.csv", index=False)

        # CSV aeropuertos vacío
        df_aero = pd.DataFrame({
            "codigo": [],
            "nombre": [],
            "localidad": [],
            "provincia": [],
            "pais": [],
            "latitud": [],
            "longitud": [],
        })
        df_aero.to_csv(tmpdir_path / "aeropuertos_limpio.csv", index=False)

        from src.backend.config import settings
        monkeypatch.setattr(settings, "DATA_PROCESSED_PATH", tmpdir_path)

        resultado = cargar_datos_desde_pipeline(db)

        assert resultado["rutas_nuevas"] == 0
        assert resultado["rutas_actualizadas"] == 1

        # Verificar actualización
        ruta_actualizada = db.query(Ruta).first()
        assert ruta_actualizada.pasajeros == 600
        assert ruta_actualizada.factor_ocupacion == 0.86
