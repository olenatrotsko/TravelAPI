from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import PlaceRepository
from .schema import ProjectPlaceCreate, ProjectPlaceUpdate
from .model import ProjectPlace
from api.projects.repository import ProjectRepository
from api.users.model import User
from core.exceptions import NotFoundError, ConflictError, ValidationError


class PlaceService:

    MAX_PLACES = 10

    def __init__(self, db: AsyncSession, external_api_service):
        self.db = db
        self._place_repo = PlaceRepository(db)
        self._project_repo = ProjectRepository(db)
        self.external_api_service = external_api_service

    async def _require_project(self, project_id: int, owner: User):
        project = await self._project_repo.get_by_id_and_owner(project_id, owner.id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")
        return project

    async def add(self, project_id: int, data: ProjectPlaceCreate, owner: User) -> ProjectPlace:
        await self._require_project(project_id, owner)

        count = await self._place_repo.count_by_project(project_id)
        if count >= self.MAX_PLACES:
            raise ValidationError(f"Project already has the maximum of {self.MAX_PLACES} places")

        if await self._place_repo.exists_by_external_id(project_id, data.external_id):
            raise ConflictError(
                f"Artwork {data.external_id} is already in this project"
            )

        artwork = await self.external_api_service.fetch(data.external_id)
        return await self._place_repo.create(project_id=project_id, **artwork)

    async def get(self, project_id: int, place_id: int, owner: User) -> ProjectPlace:
        await self._require_project(project_id, owner)
        place = await self._place_repo.get_by_id(place_id, project_id)
        if not place:
            raise NotFoundError(f"Place {place_id} not found in project {project_id}")
        return place

    async def list(self, project_id: int, owner: User) -> List[ProjectPlace]:
        await self._require_project(project_id, owner)
        return await self._place_repo.list_by_project(project_id)

    async def update(
        self, project_id: int, place_id: int, data: ProjectPlaceUpdate, owner: User
    ) -> ProjectPlace:
        place = await self.get(project_id, place_id, owner)
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return place

        for key, value in update_data.items():
            setattr(place, key, value)

        await self.db.flush()
        await self.db.refresh(place)

        await self._project_repo.sync_completed_status(project_id)
        return place
