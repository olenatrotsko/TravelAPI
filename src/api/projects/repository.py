from typing import Optional, List, Tuple
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from .model import Project
from api.places.model import ProjectPlace


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        owner_id: int,
        name: str,
        description: Optional[str],
        start_date,
    ) -> Project:
        project = Project(
            owner_id=owner_id, name=name, description=description, start_date=start_date
        )
        self.db.add(project)
        await self.db.flush()
        await self.db.refresh(project, ["places"])
        return project

    async def get_by_id(self, project_id: int) -> Optional[Project]:
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.places))
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_owner(self, project_id: int, owner_id: int) -> Optional[Project]:
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.places))
            .where(Project.id == project_id, Project.owner_id == owner_id)
        )
        return result.scalar_one_or_none()

    async def list_by_owner(
        self,
        owner_id: int,
        page: int = 1,
        size: int = 20,
        is_completed: Optional[bool] = None,
    ) -> Tuple[List[Project], int]:
        query = (
            select(Project)
            .options(selectinload(Project.places))
            .where(Project.owner_id == owner_id)
        )
        count_query = select(func.count(Project.id)).where(Project.owner_id == owner_id)

        if is_completed is not None:
            query = query.where(Project.is_completed == is_completed)
            count_query = count_query.where(Project.is_completed == is_completed)

        total = (await self.db.execute(count_query)).scalar_one()
        offset = (page - 1) * size
        result = await self.db.execute(
            query.order_by(Project.created_at.desc()).offset(offset).limit(size)
        )
        return result.scalars().all(), total

    async def update(self, project: Project, **kwargs) -> Project:
        for key, value in kwargs.items():
            setattr(project, key, value)
        await self.db.flush()
        await self.db.refresh(project, ["places", "updated_at"])
        return project

    async def delete(self, project: Project):
        await self.db.delete(project)
        await self.db.flush()

    async def sync_completed_status(self, project_id: int):
        unvisited = (
            await self.db.execute(
                select(func.count(ProjectPlace.id)).where(
                    ProjectPlace.project_id == project_id,
                    ProjectPlace.is_visited == False,
                )
            )
        ).scalar_one()

        total_places = (
            await self.db.execute(
                select(func.count(ProjectPlace.id)).where(
                    ProjectPlace.project_id == project_id
                )
            )
        ).scalar_one()

        is_completed = total_places > 0 and unvisited == 0
        await self.db.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(is_completed=is_completed)
        )
        await self.db.flush()
