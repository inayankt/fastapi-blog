from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import oauth2_scheme, verify_access_token
from core.dependencies import get_db
from modules.auth.exceptions import InvalidCredentialsError, InvalidTokenError
from modules.auth.service import AuthService
from modules.users.models import User
from modules.users.repository import UserRepository


def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthService:
    return AuthService(UserRepository(db))


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    user_id = verify_access_token(token)
    if not user_id:
        raise InvalidTokenError()

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise InvalidTokenError() from None

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id_int)
    if not user:
        raise InvalidCredentialsError("User not found")

    return user
