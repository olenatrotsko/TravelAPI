from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from .service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

async def get_current_user(
    service: AuthServiceDep,
    token: str = Depends(oauth2_scheme),
):
    return await service.extract_user_from_token(token)

CurrentUserDep = Annotated[AuthService, Depends(get_current_user)]
