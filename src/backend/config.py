"""
Configuración centralizada del backend.
Reutiliza y extiende src/config.py para el pipeline ETL.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Variables de configuración globales del backend.
    Cargadas desde .env o variables de entorno.
    """

    # FastAPI
    APP_NAME: str = "AeroPredict Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api"

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/aeropredict"
    SQLALCHEMY_POOL_SIZE: int = 20
    SQLALCHEMY_MAX_OVERFLOW: int = 40
    SQLALCHEMY_POOL_PRE_PING: bool = True

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Pipeline ETL
    DATA_PROCESSED_PATH: Path = Path(__file__).parent.parent.parent / "data" / "processed"
    
    # Hugging Face Model Registry
    HF_MODEL_REPO_ID: str = "matiasfelau/aeropredict"
    
    # Umbrales de negocio (reutilizados del pipeline)
    UMBRAL_BAJA_OCUPACION: float = 0.60
    UMBRAL_OCUPACION_ELEVADA: float = 0.85
    FACTOR_MAX_VALIDO: float = 1.05
    CRECIMIENTO_TURISTICO_PCT: float = 0.20

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
