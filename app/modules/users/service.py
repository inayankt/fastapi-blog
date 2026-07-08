from botocore.exceptions import ClientError
from fastapi import UploadFile
from PIL import UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

from core.config import settings
from core.security import hash_password
from core.storage import (
    delete_profile_image,
    process_profile_image,
    upload_profile_image,
)
from modules.posts.repository import PostRepository
from modules.users.exceptions import (
    EmailAlreadyExistsError,
    FileTooLargeError,
    ImageUploadError,
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

    async def create_user(self, username: str, email: str, password: str) -> User:
        if await self.user_repo.get_by_username(username):
            raise UsernameAlreadyExistsError()

        if await self.user_repo.get_by_email(email):
            raise EmailAlreadyExistsError()

        return await self.user_repo.create(
            username, email, hash_password(password)
        )

    async def get_posts_by_user(
        self, user_id: int, skip: int, limit: int
    ) -> tuple[User, dict]:
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

    async def update_user(self, user: User, username: str | None, email: str | None) -> User:
        if (
            username is not None
            and username.lower() != user.username.lower()
            and await self.user_repo.get_by_username(username)
        ):
            raise UsernameAlreadyExistsError()

        if (
            email is not None
            and email.lower() != user.email.lower()
            and await self.user_repo.get_by_email(email)
        ):
            raise EmailAlreadyExistsError()

        updated_user = await self.user_repo.update_details(
            user=user,
            username=username,
            email=email,
        )
        return updated_user

    async def delete_user(self, user: User) -> None:
        old_filename = user.image_file

        await self.user_repo.delete(user)

        if old_filename:
            await delete_profile_image(old_filename)

    async def upload_profile_picture(self, user: User, file: UploadFile) -> User:
        content = await file.read()
        if len(content) > settings.max_upload_size_bytes:
            raise FileTooLargeError()

        try:
            processed_bytes, new_filename = await run_in_threadpool(
                process_profile_image, content
            )
        except UnidentifiedImageError as err:
            raise InvalidImageError() from err

        try:
            await upload_profile_image(processed_bytes, new_filename)
        except ClientError as err:
            raise ImageUploadError() from err

        old_filename = user.image_file

        updated_user = await self.user_repo.update_image(user, new_filename)

        if old_filename:
            await delete_profile_image(old_filename)

        return updated_user

    async def delete_profile_picture(self, user: User) -> User:
        old_filename = user.image_file

        if old_filename is None:
            raise NoProfilePictureError()

        updated_user = await self.user_repo.update_image(user, None)

        await delete_profile_image(old_filename)

        return updated_user
