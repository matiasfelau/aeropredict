"""
Pytest configuration y fixtures para tests del backend.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.backend.database import Base, get_db
from src.backend.main import app
from src.backend.models import Usuario
from src.backend.auth import hash_password


# Crear DB en memoria para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db():
    """Fixture para obtener sesión de DB en tests."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Fixture para obtener cliente de test de FastAPI."""
    return TestClient(app)


@pytest.fixture
def usuario_admin(db):
    """Fixture para crear usuario admin."""
    admin = Usuario(
        username="admin",
        email="admin@test.local",
        password_hash=hash_password("admin123"),
        activo=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def token_admin(client, db, usuario_admin):
    """Fixture para obtener JWT token de admin."""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def headers_admin(token_admin):
    """Fixture para obtener headers con JWT token."""
    return {"Authorization": f"Bearer {token_admin}"}
