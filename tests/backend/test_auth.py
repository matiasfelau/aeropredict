"""
Tests para autenticación JWT.
"""

import pytest
from src.backend.models import Usuario
from src.backend.auth import hash_password


def test_login_exitoso(client, db, usuario_admin):
    """Test: login exitoso retorna token."""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 1800  # 30 minutos


def test_login_usuario_no_existe(client):
    """Test: login con usuario inexistente falla."""
    response = client.post(
        "/auth/login",
        json={"username": "noexiste", "password": "password123"},
    )
    assert response.status_code == 401
    assert "Credenciales inválidas" in response.json()["detail"]


def test_login_contrasena_incorrecta(client, db, usuario_admin):
    """Test: login con contraseña incorrecta falla."""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Credenciales inválidas" in response.json()["detail"]


def test_login_usuario_inactivo(client, db):
    """Test: login con usuario inactivo falla."""
    usuario_inactivo = Usuario(
        username="inactivo",
        email="inactivo@test.local",
        password_hash=hash_password("password123"),
        activo=False,
    )
    db.add(usuario_inactivo)
    db.commit()

    response = client.post(
        "/auth/login",
        json={"username": "inactivo", "password": "password123"},
    )
    assert response.status_code == 401
