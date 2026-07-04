from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.models import PasswordResetToken


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, user_id: int, token_hash: str, expires_at: str
    ) -> PasswordResetToken:
        reset_token = PasswordResetToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        self.db.add(reset_token)
        await self.db.commit()

    async def get_by_token_hash(self, token_hash) -> PasswordResetToken:
        result = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash
            )
        )
        return result.scalars().first()

    async def delete(self, reset_token: PasswordResetToken) -> None:
        await self.db.delete(reset_token)
        await self.db.commit()

    async def delete_by_user_id(self, user_id: int) -> None:
        await self.db.execute(
            delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
        )
        await self.db.commit()
