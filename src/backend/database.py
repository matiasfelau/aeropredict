"""
Configuración de base de datos y session factory.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

# Crear motor SQL
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.SQLALCHEMY_POOL_SIZE,
        max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
        pool_pre_ping=settings.SQLALCHEMY_POOL_PRE_PING,
    )

# Factory de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos ORM
Base = declarative_base()


def get_db():
    """
    Genera una sesión de DB.
    Usada como dependency en endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
