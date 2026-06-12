"""
Autenticación JWT y operaciones de seguridad.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import settings
from .models import Usuario

# Contexto de hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash una contraseña."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT access token.

    Args:
        data: Datos a incluir en el token (ej: {"sub": "username"})
        expires_delta: Tiempo de expiración. Si es None, usa ACCESS_TOKEN_EXPIRE_MINUTES

    Returns:
        JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verifica un JWT token y retorna el username si es válido.

    Args:
        token: JWT token string

    Returns:
        username si es válido, None si no
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


def get_usuario_by_username(db: Session, username: str) -> Optional[Usuario]:
    """Obtiene un usuario por username."""
    return db.query(Usuario).filter(Usuario.username == username).first()


def authenticate_usuario(db: Session, username: str, password: str) -> Optional[Usuario]:
    """
    Autentica un usuario verificando username y password.

    Returns:
        Usuario si la autenticación es exitosa, None si falla
    """
    usuario = get_usuario_by_username(db, username)
    if not usuario:
        return None
    if not verify_password(password, usuario.password_hash):
        return None
    return usuario
