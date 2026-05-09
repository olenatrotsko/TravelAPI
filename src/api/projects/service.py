import math
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import ProjectRepository
from .schema import ProjectCreate, ProjectUpdate, ProjectListItem, PaginatedProjects
from .model import Project
from core.exceptions import NotFoundError, ConflictError, ValidationError
from api.users.model import User
from api.places.repository import PlaceRepository


class ProjectService:
    def __init__(self, db: AsyncSession, external_api_service):
        self.db = db
        self._project_repo = ProjectRepository(db)
        self._place_repo = PlaceRepository(db)
        self.external_api_service = external_api_service

    async def create(self, data: ProjectCreate, owner: User) -> Project:
        fetched = []
        if data.places:
            ids = [p.external_id for p in data.places]
            if len(ids) != len(set(ids)):
                raise ValidationError("Duplicate external IDs in place list")
            for ext_id in ids:
                fetched.append(await self.external_api_service.fetch(ext_id))

        project = await self._project_repo.create(
            owner_id=owner.id,
            name=data.name,
            description=data.description,
            start_date=data.start_date,
        )

        for artwork in fetched:
            await self._place_repo.create(project_id=project.id, **artwork)

        return await self._project_repo.get_by_id(project.id)

    async def get(self, project_id: int, owner: User) -> Project:
        project = await self._project_repo.get_by_id_and_owner(project_id, owner.id)
        if not project:
            raise NotFoundError(f"Project {project_id} not found")
        return project

    async def list(
        self,
        owner: User,
        page: int,
        size: int,
        is_completed: Optional[bool],
    ) -> PaginatedProjects:
        projects, total = await self._project_repo.list_by_owner(
            owner_id=owner.id, page=page, size=size, is_completed=is_completed
        )
        pages = math.ceil(total / size) if size else 1
        items = [
            ProjectListItem(
                id=p.id,
                owner_id=p.owner_id,
                name=p.name,
                description=p.description,
                start_date=p.start_date,
                is_completed=p.is_completed,
                place_count=len(p.places),
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in projects
        ]
        return PaginatedProjects(items=items, total=total, page=page, size=size, pages=pages)

    async def update(self, project_id: int, data: ProjectUpdate, owner: User) -> Project:
        project = await self.get(project_id, owner)
        update_data = data.model_dump(exclude_unset=True)
        return await self._project_repo.update(project, **update_data)

    async def delete(self, project_id: int, owner: User):
        project = await self.get(project_id, owner)
        has_visited = await self._place_repo.has_any_visited(project_id)
        if has_visited:
            raise ConflictError(
                "Cannot delete project: one or more places have already been visited"
            )
        await self._project_repo.delete(project)
