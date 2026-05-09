from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from api.projects.service import ProjectService
from api.places.dependencies import ArticServiceDep

def get_arcic_project_service(artic_service: ArticServiceDep, db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db, artic_service)

ProjectServiceDep = Annotated[ProjectService, Depends(get_arcic_project_service)]
