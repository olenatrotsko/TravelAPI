from typing import List
from fastapi import APIRouter, status

from api.auth.dependencies import CurrentUserDep
from .schema import ProjectPlaceCreate, ProjectPlaceUpdate, ProjectPlaceResponse
from .dependencies import PlaceServiceDep

router = APIRouter(prefix="/projects/{project_id}/places", tags=["Places"])


@router.post("", response_model=ProjectPlaceResponse, status_code=status.HTTP_201_CREATED)
async def add_place(
    project_id: int,
    data: ProjectPlaceCreate,
    current_user: CurrentUserDep,
    service: PlaceServiceDep,
):
    return await service.add(project_id, data, current_user)


@router.get("", response_model=List[ProjectPlaceResponse], status_code=status.HTTP_200_OK)
async def list_places(
    project_id: int,
    current_user: CurrentUserDep,
    service: PlaceServiceDep,
):
    return await service.list(project_id, current_user)


@router.get("/{place_id}", response_model=ProjectPlaceResponse, status_code=status.HTTP_200_OK)
async def get_place(
    project_id: int,
    place_id: int,
    current_user: CurrentUserDep,
    service: PlaceServiceDep,
):
    return await service.get(project_id, place_id, current_user)


@router.patch("/{place_id}", response_model=ProjectPlaceResponse, status_code=status.HTTP_200_OK)
async def update_place(
    project_id: int,
    place_id: int,
    data: ProjectPlaceUpdate,
    current_user: CurrentUserDep,
    service: PlaceServiceDep,
):
    return await service.update(project_id, place_id, data, current_user)
