from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from .model import ProjectPlace


class PlaceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        project_id: int,
        external_id: int,
        title: str,
        artist_display: Optional[str],
        place_of_origin: Optional[str],
        image_url: Optional[str],
    ) -> ProjectPlace:
        place = ProjectPlace(
            project_id=project_id,
            external_id=external_id,
            title=title,
            artist_display=artist_display,
            place_of_origin=place_of_origin,
            image_url=image_url,
        )
        self.db.add(place)
        await self.db.flush()
        await self.db.refresh(place)
        return place

    async def get_by_id(self, place_id: int, project_id: int) -> Optional[ProjectPlace]:
        result = await self.db.execute(
            select(ProjectPlace).where(
                ProjectPlace.id == place_id, ProjectPlace.project_id == project_id
            )
        )
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: int) -> List[ProjectPlace]:
        result = await self.db.execute(
            select(ProjectPlace)
            .where(ProjectPlace.project_id == project_id)
            .order_by(ProjectPlace.created_at.asc())
        )
        return result.scalars().all()

    async def count_by_project(self, project_id: int) -> int:
        result = await self.db.execute(
            select(func.count(ProjectPlace.id)).where(ProjectPlace.project_id == project_id)
        )
        return result.scalar_one()

    async def exists_by_external_id(self, project_id: int, external_id: int) -> bool:
        result = await self.db.execute(
            select(func.count(ProjectPlace.id)).where(
                ProjectPlace.project_id == project_id,
                ProjectPlace.external_id == external_id,
            )
        )
        return result.scalar_one() > 0

    async def has_any_visited(self, project_id: int) -> bool:
        result = await self.db.execute(
            select(func.count(ProjectPlace.id)).where(
                ProjectPlace.project_id == project_id,
                ProjectPlace.is_visited == True,
            )
        )
        return result.scalar_one() > 0
