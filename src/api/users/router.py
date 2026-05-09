from fastapi import APIRouter, status

from .dependencies import UserServiceDep
from .schema import UserProfileResponse, UserProfileUpdate
from .service import UserService
from api.auth.dependencies import CurrentUserDep


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", status_code=status.HTTP_200_OK, response_model=UserProfileResponse)
async def get_profile(current_user: CurrentUserDep):
    """Get the currently authenticated user's profile."""
    return current_user


@router.patch("/profile", status_code=status.HTTP_200_OK, response_model=UserProfileResponse)
async def update_me(
    data: UserProfileUpdate,
    current_user: CurrentUserDep,
    service: UserServiceDep,
):
    """Update the current user's email or username."""
    return await service.update_profile(current_user, data)
