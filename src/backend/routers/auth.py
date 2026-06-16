"""
Router de autenticación.

Endpoints:
- POST /auth/login — autentica usuario y retorna JWT token
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import authenticate_usuario, create_access_token
from ..database import get_db
from ..schemas import LoginRequest, TokenResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Autentica un usuario y retorna un JWT access token.

    Args:
        request: LoginRequest con username y password

    Returns:
        TokenResponse con access_token, token_type y expires_in

    Raises:
        401: Si las credenciales son inválidas
    """
    usuario = authenticate_usuario(db, request.username, request.password)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    # Crear token
    access_token = create_access_token(data={"sub": usuario.username})

    return TokenResponse(
        access_token=access_token,
        expires_in=30 * 60,  # 30 minutos en segundos
    )
