from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create(
        self, username: str, email: str, image_file: str | None = None
    ) -> User:
        new_user = User(username=username, email=email, image_file=image_file)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update(
        self,
        user: User,
        username: str | None = None,
        email: str | None = None,
        image_file: str | None = None,
    ) -> User:
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if image_file is not None:
            user.image_file = image_file
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()
