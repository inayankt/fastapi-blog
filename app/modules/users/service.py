from auth import hash_password
from modules.users.exceptions import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from modules.users.models import User
from modules.users.repository import UserRepository
from modules.users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repo = repository

    async def get_user(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def create_user(self, payload: UserCreate) -> User:
        if await self.repo.get_by_username(payload.username):
            raise UsernameAlreadyExistsError()

        if await self.repo.get_by_email(payload.email):
            raise EmailAlreadyExistsError()

        return await self.repo.create(
            payload.username, payload.email, hash_password(payload.password)
        )

    async def update_user(self, user: User, payload: UserUpdate) -> User:
        if (
            payload.username is not None
            and payload.username.lower() != user.username.lower()
            and await self.repo.get_by_username(payload.username)
        ):
            raise UsernameAlreadyExistsError()

        if (
            payload.email is not None
            and payload.email.lower() != user.email.lower()
            and await self.repo.get_by_email(payload.email)
        ):
            raise EmailAlreadyExistsError()

        updated_user = await self.repo.update(
            user=user,
            username=payload.username,
            email=payload.email,
            image_file=payload.image_file,
        )
        return updated_user

    async def delete_user(self, user: User) -> None:
        await self.repo.delete(user)
