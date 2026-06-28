from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db
from modules.posts.repository import PostRepository
from modules.posts.service import PostService
from modules.users.repository import UserRepository


def get_post_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PostService:
    return PostService(UserRepository(db), PostRepository(db))
