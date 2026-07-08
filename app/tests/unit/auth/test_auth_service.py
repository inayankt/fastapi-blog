from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import BackgroundTasks

from modules.auth.exceptions import (
    IncorrectCurrentPasswordError,
    InvalidCredentialsError,
    InvalidResetTokenError,
    InvalidTokenError,
)
from modules.auth.service import AuthService
from modules.users.models import User


@pytest.fixture
def repos_and_svc():
    auth_repo = AsyncMock()
    user_repo = AsyncMock()
    svc = AuthService(auth_repo=auth_repo, user_repo=user_repo)
    return auth_repo, user_repo, svc


@pytest.mark.anyio
async def test_login_success(repos_and_svc):
    _, user_repo, svc = repos_and_svc
    user = User(
        id=1,
        username="test",
        email="test@test.com",
        password_hash="hashed-password",
    )
    user_repo.get_by_email.return_value = user

    with (
        patch("modules.auth.service.verify_password", return_value=True),
        patch("modules.auth.service.create_access_token") as mock_create,
    ):
        result = await svc.login(email="test@test.com", password="password")

        assert result["token_type"] == "bearer"
        assert "access_token" in result
        mock_create.assert_called_once()


@pytest.mark.anyio
async def test_login_not_registered(repos_and_svc):
    _, user_repo, svc = repos_and_svc
    user_repo.get_by_email.return_value = None

    with patch("modules.auth.service.create_access_token") as mock_create:
        with pytest.raises(InvalidCredentialsError):
            await svc.login(email="test@test.com", password="password")
        
        mock_create.assert_not_called()


@pytest.mark.anyio
async def test_login_incorrect_password(repos_and_svc):
    _, user_repo, svc = repos_and_svc
    user = User(
        id=1,
        username="test",
        email="test@test.com",
        password_hash="hashed-password",
    )
    user_repo.get_by_email.return_value = user
    
    with (
        patch("modules.auth.service.verify_password", return_value=False),
        patch("modules.auth.service.create_access_token") as mock_create,
    ):
        with pytest.raises(InvalidCredentialsError):
            await svc.login(email="test@test.com", password="password")
        
        mock_create.assert_not_called()


@pytest.mark.anyio
async def test_get_current_user_success(repos_and_svc):
    _, user_repo, svc = repos_and_svc
    user = User(id=1, username="test", email="test@test.com", password_hash="hash")
    user_repo.get_by_id.return_value = user

    with patch("modules.auth.service.verify_access_token", return_value=f"{user.id}"):
        result = await svc.get_current_user(token="valid-token")

    assert result == user


@pytest.mark.anyio
@pytest.mark.parametrize(
    "token_sub",
    [
        None,
        "abc",
    ],
)
async def test_get_current_user_invalid_token(repos_and_svc, token_sub):
    _, _, svc = repos_and_svc

    with patch("modules.auth.service.verify_access_token", return_value=token_sub):
        with pytest.raises(InvalidTokenError):
            await svc.get_current_user(token="invalid-token")


@pytest.mark.anyio
async def test_get_current_user_not_found(repos_and_svc):
    _, user_repo, svc = repos_and_svc
    user_repo.get_by_id.return_value = None
    
    with patch("modules.auth.service.verify_access_token", return_value=f"999"):
        with pytest.raises(InvalidCredentialsError):
            await svc.get_current_user(token="invalid-token")


@pytest.mark.anyio
async def test_handle_forgot_password(repos_and_svc):
    auth_repo, user_repo, svc = repos_and_svc
    user = User(id=1, username="test", email="test@test.com", password_hash="hash")
    user_repo.get_by_email.return_value = user

    with (
        patch("modules.auth.service.generate_reset_token", return_value="reset-token"),
        patch("modules.auth.service.hash_reset_token", return_value="hashed-token"),
        patch("modules.auth.service.send_password_reset_email", new_callable=AsyncMock) as mock_send,
    ):
        bg_tasks = BackgroundTasks()
        result = await svc.handle_forgot_password(email="test@test.com", bg_tasks=bg_tasks)

        assert "message" in result
        auth_repo.delete_by_user_id.assert_awaited_once_with(user.id)
        auth_repo.create.assert_awaited_once()
        mock_send.assert_not_called()


@pytest.mark.anyio
async def test_handle_reset_password_success(repos_and_svc):
    auth_repo, user_repo, svc = repos_and_svc
    user = User(id=1, username="test", email="test@test.com", password_hash="hash")
    reset_token = type(
        "PasswordResetToken",
        (),
        {"token_hash": "hashed-token", "user_id": 1, "expires_at": datetime.now(UTC) + timedelta(minutes=10)},
    )()
    auth_repo.get_by_token_hash.return_value = reset_token
    user_repo.get_by_id.return_value = user

    with (
        patch("modules.auth.service.hash_reset_token", return_value="hashed-token"),
        patch("modules.auth.service.hash_password", return_value="new-hash"),
    ):
        result = await svc.handle_reset_password(new_password="new-password", token="token")

        assert "message" in result
        user_repo.update_password.assert_awaited_once()
        auth_repo.delete_by_user_id.assert_awaited_once_with(user.id)


@pytest.mark.anyio
async def test_handle_reset_password_invalid_token(repos_and_svc):
    auth_repo, user_repo, svc = repos_and_svc
    auth_repo.get_by_token_hash.return_value = None

    with pytest.raises(InvalidResetTokenError):
        await svc.handle_reset_password(new_password="new-password", token="token")
    
    user_repo.update_password.assert_not_awaited()
    auth_repo.delete_by_user_id.assert_not_awaited()


@pytest.mark.anyio
async def test_handle_reset_password_expired_token(repos_and_svc):
    auth_repo, user_repo, svc = repos_and_svc
    auth_repo.get_by_token_hash.return_value = type(
        "PasswordResetToken",
        (),
        {"token_hash": "hashed-token", "user_id": 1, "expires_at": datetime.now(UTC) - timedelta(minutes=5)},
    )()

    with pytest.raises(InvalidResetTokenError):
        await svc.handle_reset_password(new_password="new-password", token="token")
    
    user_repo.update_password.assert_not_awaited()
    auth_repo.delete_by_user_id.assert_not_awaited()


@pytest.mark.anyio
async def test_handle_change_password_success(repos_and_svc):
    auth_repo, user_repo, svc = repos_and_svc
    user = User(id=1, username="test", email="test@test.com", password_hash="hash")
    user_repo.update_password.return_value = user

    with (
        patch("modules.auth.service.verify_password", return_value=True),
        patch("modules.auth.service.hash_password", return_value="new-hash"),
    ):
        result = await svc.handle_change_password(
            user=user,
            current_password="old",
            new_password="new",
        )

        assert "message" in result
        user_repo.update_password.assert_awaited_once()
        auth_repo.delete_by_user_id.assert_awaited_once_with(user.id)


@pytest.mark.anyio
async def test_handle_change_password_incorrect_current_password(repos_and_svc):
    auth_repo, user_repo, svc = repos_and_svc
    user = User(id=1, username="test", email="test@test.com", password_hash="hash")

    with patch("modules.auth.service.verify_password", return_value=False):
        with pytest.raises(IncorrectCurrentPasswordError):
            await svc.handle_change_password(
                user=user,
                current_password="wrong",
                new_password="new",
            )

    user_repo.update_password.assert_not_awaited()
    auth_repo.delete_by_user_id.assert_not_awaited()
