from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import oauth2_scheme
from db import get_db
from modules.auth.exceptions import NotCurrentUserError, NotPostOwnerError
from modules.auth.service import AuthService
from modules.posts.dependencies import get_post_service
from modules.posts.models import Post
from modules.posts.service import PostService
from modules.users.dependencies import get_user_service
from modules.users.models import User
from modules.users.repository import UserRepository
from modules.users.service import UserService


def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthService:
    return AuthService(UserRepository(db))


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    return await service.get_current_user(token)


async def is_post_owner(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    post_service: Annotated[PostService, Depends(get_post_service)],
) -> Post:
    post = await post_service.get_post(post_id)
    if post.user_id != current_user.id:
        raise NotPostOwnerError()
    return post


async def is_valid_current_user(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    user = await user_service.get_user(user_id)
    if user.id != current_user.id:
        raise NotCurrentUserError()
    return user
