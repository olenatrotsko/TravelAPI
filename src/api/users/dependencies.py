
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import UserService
from core.database import get_db


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]
