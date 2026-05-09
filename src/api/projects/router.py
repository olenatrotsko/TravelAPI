from typing import Optional
from fastapi import APIRouter, Query, status

from api.projects.schema import PaginatedProjects, ProjectCreate, ProjectResponse, ProjectUpdate
from api.auth.dependencies import CurrentUserDep
from api.projects.dependencies import ProjectServiceDep


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    current_user: CurrentUserDep,
    service: ProjectServiceDep,
):
    """Create a travel project. Optionally include places from Art Institute API."""
    return await service.create(data, current_user)


@router.get("/", response_model=PaginatedProjects)
async def list_projects(
    current_user: CurrentUserDep,
    service: ProjectServiceDep,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    is_completed: Optional[bool] = Query(None),

):
    """List the current user's projects with pagination and optional completion filter."""
    return await service.list(current_user, page=page, size=size, is_completed=is_completed)


@router.get("/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
async def get_project(
    project_id: int,
    current_user: CurrentUserDep,
    service: ProjectServiceDep,
):
    """Get a single project (must belong to current user)."""
    return await service.get(project_id, current_user)


@router.patch("/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: CurrentUserDep,
    service: ProjectServiceDep,
):
    """Update project name, description, or start date."""
    return await service.update(project_id, data, current_user)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: CurrentUserDep,
    service: ProjectServiceDep,
):
    """Delete a project. Blocked if any place is already visited."""
    await service.delete(project_id, current_user)
