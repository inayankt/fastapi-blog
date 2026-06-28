from modules.users.exceptions import (
    EmailAlreadyExistsError,
    UserNotFoundError,
    UsernameAlreadyExistsError,
)
from modules.users.models import User
from modules.users.repository import UserRepository
from modules.users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repo = repository

    def get_user(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    def create_user(self, payload: UserCreate) -> User:
        if self.repo.get_by_username(payload.username):
            raise UsernameAlreadyExistsError()

        if self.repo.get_by_email(payload.email):
            raise EmailAlreadyExistsError()

        return self.repo.create(payload.username, payload.email)

    def update_user(self, user_id: int, payload: UserUpdate) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        if payload.username is not None and self.repo.get_by_username(payload.username):
            raise UsernameAlreadyExistsError()

        if payload.email is not None and self.repo.get_by_email(payload.email):
            raise EmailAlreadyExistsError()

        updated_user = self.repo.update(
            user=user,
            username=payload.username,
            email=payload.email,
            image_file=payload.image_file,
        )
        return updated_user

    def delete_user(self, user_id: int) -> None:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        self.repo.delete(user)
