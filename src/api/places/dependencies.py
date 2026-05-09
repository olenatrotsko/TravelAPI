from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from .service import PlaceService
from .artic import ArticService


def get_artic_service():
    return ArticService()

ArticServiceDep = Annotated[ArticService, Depends(get_artic_service)]


def get_artic_place_service(artic_service: ArticServiceDep, db: AsyncSession = Depends(get_db)) -> PlaceService:
    return PlaceService(db, artic_service)

PlaceServiceDep = Annotated[PlaceService, Depends(get_artic_place_service)]
