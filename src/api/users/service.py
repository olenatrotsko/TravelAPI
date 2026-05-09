from sqlalchemy.ext.asyncio import AsyncSession

from .repository import UserRepository
from .schema import UserProfileUpdate
from .model import User
from core.exceptions import ConflictError


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._repo = UserRepository(db)

    async def get_profile(self, user: User) -> User:
        return user

    async def update_profile(self, user: User, data: UserProfileUpdate) -> User:
        if data.email:
            existing = await self._repo.get_by_email(data.email)
            if existing and existing.id != user.id:
                raise ConflictError("Email is already in use")
        if data.username:
            existing = await self._repo.get_by_username(data.username)
            if existing and existing.id != user.id:
                raise ConflictError("Username is already taken")
        return await self._repo.update(user, **data.model_dump(exclude_unset=True))
