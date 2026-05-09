from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from .model import RevokedToken


class RevokedTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self,
        jwt: str,
        expires_at: datetime,
    ) -> RevokedToken:

        token = RevokedToken(
            token=jwt,
            expires_at=expires_at,
        )

        self.db.add(token)
        await self.db.flush()
        await self.db.refresh(token)
        return token

    async def is_revoked(self, jwt: str) -> bool:
        result = await self.db.execute(select(RevokedToken).where(RevokedToken.token == jwt)) 
        return result.scalar_one_or_none() is not None
