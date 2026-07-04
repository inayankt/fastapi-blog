from datetime import UTC, datetime, timedelta

from fastapi import BackgroundTasks

from core.config import settings
from core.mail import send_password_reset_email
from core.security import (
    create_access_token,
    generate_reset_token,
    hash_password,
    hash_reset_token,
    verify_access_token,
    verify_password,
)
from modules.auth.exceptions import (
    IncorrectCurrentPasswordError,
    InvalidCredentialsError,
    InvalidResetTokenError,
    InvalidTokenError,
)
from modules.auth.repository import AuthRepository
from modules.users.models import User
from modules.users.repository import UserRepository


class AuthService:
    def __init__(self, auth_repo: AuthRepository, user_repo: UserRepository):
        self.auth_repo = auth_repo
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

    async def handle_forgot_password(
        self, email: str, background_tasks: BackgroundTasks
    ) -> dict:
        user = await self.user_repo.get_by_email(email)

        if user:
            await self.auth_repo.delete_by_user_id(user.id)

            token = generate_reset_token()
            token_hash = hash_reset_token(token)
            expires_at = datetime.now(UTC) + timedelta(
                minutes=settings.reset_token_expire_minutes
            )

            await self.auth_repo.create(
                user_id=user.id, token_hash=token_hash, expires_at=expires_at
            )

            background_tasks.add_task(
                send_password_reset_email,
                to_email=user.email,
                username=user.username,
                token=token,
            )

        return {
            "message": "If an account exists with this email, you will receive password reset instructions"
        }

    async def handle_reset_password(self, new_password: str, token: str) -> dict:
        token_hash = hash_reset_token(token)

        reset_token = await self.auth_repo.get_by_token_hash(token_hash)

        if not reset_token:
            raise InvalidResetTokenError()

        if reset_token.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
            await self.auth_repo.delete(reset_token)
            raise InvalidResetTokenError()

        user = await self.user_repo.get_by_id(reset_token.user_id)
        if not user:
            raise InvalidResetTokenError()

        await self.user_repo.update_password(user, hash_password(new_password))
        await self.auth_repo.delete_by_user_id(user.id)

        return {
            "message": "Password reset successfully, you can now log in with your new password"
        }

    async def handle_change_password(
        self, user: User, current_password: str, new_password: str
    ) -> dict:
        if not verify_password(current_password, user.password_hash):
            raise IncorrectCurrentPasswordError()

        await self.user_repo.update_password(user, hash_password(new_password))
        await self.auth_repo.delete_by_user_id(user.id)

        return {"message": "Password changed successfully"}
