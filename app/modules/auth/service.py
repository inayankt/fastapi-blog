from datetime import timedelta

from auth import create_access_token, verify_password
from config import settings
from modules.auth.exceptions import InvalidCredentialsError
from modules.users.repository import UserRepository


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def login(self, email: str, password: str) -> str:
        user = await self.repo.get_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
