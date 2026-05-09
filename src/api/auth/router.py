from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from .dependencies import AuthServiceDep
from .schema import UserRegister, UserResponse, TokenResponse


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    service: AuthServiceDep,
):
    """Register a new user account."""
    return await service.register(data)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    service: AuthServiceDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Login with email + password, receive a JWT access token."""
    token = await service.login(email=form_data.username, password=form_data.password)
    return TokenResponse(access_token=token)
