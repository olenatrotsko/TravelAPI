import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext

from .schema import UserRegister
from .repository import RevokedTokenRepository
from api.users.model import User
from api.users.repository import UserRepository
from core.config import settings
from core.exceptions import ConflictError, UnauthorizedError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._user_repo = UserRepository(db)
        self._token_repo = RevokedTokenRepository(db)

    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def _decode_token(self, token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise UnauthorizedError
            return user_id
        except DecodeError:
            raise UnauthorizedError
        except ExpiredSignatureError:
            raise UnauthorizedError("Token expired")

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    async def extract_user_from_token(self, token: str) -> User:
        if await self._token_repo.is_revoked(token):
            raise UnauthorizedError

        user_id = self._decode_token(token)

        user = await self._user_repo.get_by_id(int(user_id))
        if user is None:
            raise UnauthorizedError
        return user

    async def register(self, data: UserRegister) -> User:
        if await self._user_repo.get_by_email(data.email):
            raise ConflictError("Email is already registered")
        if await self._user_repo.get_by_username(data.username):
            raise ConflictError("Username is already taken")
        hashed = self._hash_password(data.password)
        return await self._user_repo.create(
            email=data.email, username=data.username, hashed_password=hashed
        )

    async def login(self, email: str, password: str) -> str:
        user = await self._user_repo.get_by_email(email)
        if not user or not self._verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")
        return self._create_access_token({"sub": str(user.id)})

    async def logout(self, token: str):
        return self._token_repo.create(token)
