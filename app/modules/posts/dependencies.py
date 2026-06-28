from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db
from modules.posts.repository import PostRepository
from modules.posts.service import PostService
from modules.users.repository import UserRepository


def get_post_service(
    db: Annotated[Session, Depends(get_db)],
) -> PostService:
    return PostService(UserRepository(db), PostRepository(db))
