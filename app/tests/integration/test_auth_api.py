from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.utils import (
    auth_header,
    create_test_user,
    login_user,
)


@pytest.mark.anyio
async def test_login_success(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/auth/token",
        data={"username": "test@test.com", "password": "testpass123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data


@pytest.mark.anyio
async def test_login_invalid_credentials(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/auth/token",
        data={"username": "test@test.com", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect credentials"


@pytest.mark.anyio
async def test_get_me_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.get(
        "/api/auth/me",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@test.com"
    assert data["username"] == "testuser"
    assert "id" in data
    assert "image_path" in data


@pytest.mark.anyio
async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_forgot_password_sends_email(client: AsyncClient):
    await create_test_user(client)

    with patch(
        "modules.auth.service.send_password_reset_email",
        new_callable=AsyncMock,
    ) as mock_send:
        response = await client.post(
            "/api/auth/forgot-password",
            json={"email": "test@test.com"},
        )

        assert response.status_code == 202
        assert response.json()["message"].startswith(
            "If an account exists with this email"
        )

        mock_send.assert_awaited_once()
        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["to_email"] == "test@test.com"
        assert call_kwargs["username"] == "testuser"
        assert "token" in call_kwargs


@pytest.mark.anyio
async def test_forgot_password_unknown_email_returns_202(client: AsyncClient):
    response = await client.post(
        "/api/auth/forgot-password",
        json={"email": "missing@test.com"},
    )

    assert response.status_code == 202
    assert response.json()["message"].startswith(
        "If an account exists with this email"
    )


@pytest.mark.anyio
async def test_reset_password_success(client: AsyncClient):
    await create_test_user(client)

    with patch(
        "modules.auth.service.send_password_reset_email",
        new_callable=AsyncMock,
    ) as mock_send:
        response = await client.post(
            "/api/auth/forgot-password",
            json={"email": "test@test.com"},
        )

        assert response.status_code == 202
        mock_send.assert_awaited_once()
        token = mock_send.call_args.kwargs["token"]

    response = await client.post(
        "/api/auth/reset-password",
        json={"token": token, "new_password": "newpass123"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successfully, you can now log in with your new password"

    login_response = await client.post(
        "/api/auth/token",
        data={"username": "test@test.com", "password": "newpass123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


@pytest.mark.anyio
async def test_reset_password_invalid_token(client: AsyncClient):
    response = await client.post(
        "/api/auth/reset-password",
        json={"token": "invalid-token", "new_password": "newpass123"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired reset token"


@pytest.mark.anyio
async def test_change_password_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.patch(
        "/api/auth/me/password",
        json={"current_password": "testpass123", "new_password": "newpass123"},
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"

    login_response = await client.post(
        "/api/auth/token",
        data={"username": "test@test.com", "password": "newpass123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


@pytest.mark.anyio
async def test_change_password_incorrect_current_password(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.patch(
        "/api/auth/me/password",
        json={"current_password": "wrongpass", "new_password": "newpass123"},
        headers=auth_header(token),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Current password is incorrect"
