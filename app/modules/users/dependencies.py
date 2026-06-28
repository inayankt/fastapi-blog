from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db
from modules.users.repository import UserRepository
from modules.users.service import UserService


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
) -> UserService:
    return UserService(UserRepository(db))
