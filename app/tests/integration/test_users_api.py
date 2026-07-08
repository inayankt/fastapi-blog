from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.utils import (
    auth_header,
    create_test_user,
    login_user,
)


@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
        },
    )
    assert response.status_code == 422
    assert "email" in response.text
    assert "password" in response.text


@pytest.mark.anyio
async def test_create_user_duplicate_email(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/users",
        json={
            "username": "different_user",
            "email": "test@test.com",
            "password": "password123",
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already exists"


@pytest.mark.anyio
async def test_create_user_success(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@test.com"
    assert "id" in data
    assert "image_path" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.anyio
async def test_create_user_duplicate_username(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "other@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Username already exists"


@pytest.mark.anyio
async def test_get_user_success(client: AsyncClient):
    user = await create_test_user(client)

    response = await client.get(f"/api/users/{user['id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user["id"]
    assert data["username"] == "testuser"
    assert "email" not in data
    assert "image_path" in data


@pytest.mark.anyio
async def test_get_user_not_found(client: AsyncClient):
    response = await client.get("/api/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.anyio
async def test_get_user_posts_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    for i in range(2):
        response = await client.post(
            "/api/posts",
            json={"title": f"Post {i}", "content": f"Content {i}"},
            headers=headers,
        )
        assert response.status_code == 201

    response = await client.get(f"/api/users/{user['id']}/posts")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 2
    assert len(data["posts"]) == 2
    assert data["has_more"] is False


@pytest.mark.anyio
async def test_update_user_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    response = await client.patch(
        f"/api/users/{user['id']}",
        json={"username": "updateduser", "email": "updated@test.com"},
        headers=auth_header(token),
    )
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "updateduser"
    assert data["email"] == "updated@test.com"


@pytest.mark.anyio
async def test_update_user_duplicate_username(client: AsyncClient):
    await create_test_user(client)
    other_user = await create_test_user(client, username="other", email="other@test.com")
    token = await login_user(client, email="other@test.com")

    response = await client.patch(
        f"/api/users/{other_user['id']}",
        json={"username": "testuser"},
        headers=auth_header(token),
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Username already exists"


@pytest.mark.anyio
async def test_update_user_duplicate_email(client: AsyncClient):
    await create_test_user(client)
    other_user = await create_test_user(client, username="other", email="other@test.com")
    token = await login_user(client, email="other@test.com")

    response = await client.patch(
        f"/api/users/{other_user['id']}",
        json={"email": "test@test.com"},
        headers=auth_header(token),
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already exists"


@pytest.mark.anyio
async def test_update_user_wrong_user(client: AsyncClient):
    user1 = await create_test_user(client, username="user1", email="user1@test.com")
    token1 = await login_user(client, email="user1@test.com")

    user2 = await create_test_user(client, username="user2", email="user2@test.com")
    token2 = await login_user(client, email="user2@test.com")

    response = await client.patch(
        f"/api/users/{user1['id']}",
        json={"username": "hacked"},
        headers=auth_header(token2),
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to alter this user"


@pytest.mark.anyio
async def test_update_user_unauthenticated(client: AsyncClient):
    user = await create_test_user(client)

    response = await client.patch(
        f"/api/users/{user['id']}",
        json={"username": "updateduser"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_delete_user_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    response = await client.delete(
        f"/api/users/{user['id']}",
        headers=auth_header(token),
    )
    assert response.status_code == 204

    get_response = await client.get(f"/api/users/{user['id']}")
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_delete_user_wrong_user(client: AsyncClient):
    user1 = await create_test_user(client, username="user1", email="user1@test.com")
    user2 = await create_test_user(client, username="user2", email="user2@test.com")
    token2 = await login_user(client, email="user2@test.com")

    response = await client.delete(
        f"/api/users/{user1['id']}",
        headers=auth_header(token2),
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to alter this user"


@pytest.mark.anyio
async def test_delete_user_unauthenticated(client: AsyncClient):
    user = await create_test_user(client)

    response = await client.delete(f"/api/users/{user['id']}")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_delete_profile_picture_success(client: AsyncClient, mocked_s3):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    test_image_path = Path(__file__).parent.parent / "data" / "test_image.jpg"
    image_bytes = test_image_path.read_bytes()

    upload_response = await client.patch(
        f"/api/users/{user['id']}/picture",
        files={"file": ("profile.jpg", BytesIO(image_bytes), "image/jpeg")},
        headers=headers,
    )
    assert upload_response.status_code == 200
    
    data = upload_response.json()
    assert data["image_file"] is not None
    assert data["image_file"].endswith(".jpg")
    assert "s3" in data["image_path"]
    
    s3_objects = mocked_s3.list_objects_v2(Bucket="test-bucket")
    assert "Contents" in s3_objects
    assert len(s3_objects["Contents"]) == 1
    assert s3_objects["Contents"][0]["Key"].endswith(data["image_file"])

    delete_response = await client.delete(
        f"/api/users/{user['id']}/picture",
        headers=headers,
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["image_file"] is None

    s3_objects = mocked_s3.list_objects_v2(Bucket="test-bucket")
    assert "Contents" not in s3_objects


@pytest.mark.anyio
async def test_delete_profile_picture_no_image(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    response = await client.delete(
        f"/api/users/{user['id']}/picture",
        headers=auth_header(token),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Profile picture does not exist"
