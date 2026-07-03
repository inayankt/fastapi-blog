from fastapi import UploadFile
from PIL import UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

from core.config import settings
from core.security import hash_password
from core.storage import delete_profile_image, process_profile_image
from modules.posts.repository import PostRepository
from modules.users.exceptions import (
    EmailAlreadyExistsError,
    FileTooLargeError,
    InvalidImageError,
    NoProfilePictureError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from modules.users.models import User
from modules.users.repository import UserRepository
from modules.users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        post_repository: PostRepository,
    ):
        self.user_repo = user_repository
        self.post_repo = post_repository

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def create_user(self, payload: UserCreate) -> User:
        if await self.user_repo.get_by_username(payload.username):
            raise UsernameAlreadyExistsError()

        if await self.user_repo.get_by_email(payload.email):
            raise EmailAlreadyExistsError()

        return await self.user_repo.create(
            payload.username, payload.email, hash_password(payload.password)
        )

    async def get_posts_by_user(self, user_id: int, skip: int, limit: int):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        total = await self.post_repo.count_by_user(user_id)
        posts = await self.post_repo.get_by_user_id(user_id, skip, limit)
        has_more = skip + len(posts) < total
        return user, {
            "posts": posts,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": has_more,
        }

    async def update_user(self, user: User, payload: UserUpdate) -> User:
        if (
            payload.username is not None
            and payload.username.lower() != user.username.lower()
            and await self.user_repo.get_by_username(payload.username)
        ):
            raise UsernameAlreadyExistsError()

        if (
            payload.email is not None
            and payload.email.lower() != user.email.lower()
            and await self.user_repo.get_by_email(payload.email)
        ):
            raise EmailAlreadyExistsError()

        updated_user = await self.user_repo.update_details(
            user=user,
            username=payload.username,
            email=payload.email,
        )
        return updated_user

    async def delete_user(self, user: User) -> None:
        old_filename = user.image_file

        await self.user_repo.delete(user)

        if old_filename:
            delete_profile_image(old_filename)

    async def upload_profile_picture(self, user: User, file: UploadFile) -> User:
        content = await file.read()
        if len(content) > settings.max_upload_size_bytes:
            raise FileTooLargeError()

        try:
            new_filename = await run_in_threadpool(process_profile_image, content)
        except UnidentifiedImageError as err:
            raise InvalidImageError() from err

        old_filename = user.image_file

        updated_user = await self.user_repo.update_image(user, new_filename)

        if old_filename:
            delete_profile_image(old_filename)

        return updated_user

    async def delete_profile_picture(self, user: User) -> User:
        old_filename = user.image_file

        if old_filename is None:
            raise NoProfilePictureError()

        updated_user = await self.user_repo.update_image(user, None)

        delete_profile_image(old_filename)

        return updated_user
