"""
Dependencies para FastAPI (inyección de dependencias).
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .auth import verify_token
from .database import SessionLocal, get_db
from .models import Usuario

# Security scheme
security = HTTPBearer()


async def get_current_usuario(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> Usuario:
    """
    Dependency que verifica el JWT token y retorna el usuario autenticado.

    Lanza HTTPException 401 si el token es inválido.
    """
    token = credentials.credentials
    username = verify_token(token)

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = db.query(Usuario).filter(Usuario.username == username).first()
    if usuario is None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario


async def get_current_usuario_optional(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)] = None,
) -> Optional[Usuario]:
    """
    Dependency que verifica el JWT token pero no requiere autenticación.
    Retorna el usuario si el token es válido, None si no hay token.
    """
    if credentials is None:
        return None

    token = credentials.credentials
    username = verify_token(token)

    if username is None:
        return None

    usuario = db.query(Usuario).filter(Usuario.username == username).first()
    if usuario is None or not usuario.activo:
        return None

    return usuario
