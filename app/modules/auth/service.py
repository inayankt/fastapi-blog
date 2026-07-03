from datetime import timedelta

from core.config import settings
from core.security import create_access_token, verify_access_token, verify_password
from modules.auth.exceptions import InvalidCredentialsError, InvalidTokenError
from modules.users.models import User
from modules.users.repository import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def login(self, email: str, password: str) -> str:
        user = await self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    async def get_current_user(self, token: str) -> User:
        user_id = verify_access_token(token)
        if not user_id:
            raise InvalidTokenError()

        try:
            user_id_int = int(user_id)
        except (TypeError, ValueError):
            raise InvalidTokenError() from None

        user = await self.user_repo.get_by_id(user_id_int)
        if not user:
            raise InvalidCredentialsError("User not found")

        return user
