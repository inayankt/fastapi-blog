import pytest
from httpx import AsyncClient

from tests.utils import (
    auth_header,
    create_test_user,
    login_user,
)


@pytest.mark.anyio
async def test_get_posts_empty(client: AsyncClient):
    response = await client.get("/api/posts")
    assert response.status_code == 200
    
    data = response.json()
    assert data["posts"] == []
    assert data["total"] == 0
    assert data["has_more"] is False


@pytest.mark.anyio
async def test_get_post_not_found(client: AsyncClient):
    response = await client.get("/api/posts/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


@pytest.mark.anyio
async def test_get_post_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    create_response = await client.post(
        "/api/posts",
        json={"title": "Test Post", "content": "Test content"},
        headers=headers,
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    response = await client.get(f"/api/posts/{post_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == post_id
    assert data["title"] == "Test Post"
    assert data["content"] == "Test content"
    assert data["author"]["username"] == "testuser"


@pytest.mark.anyio
async def test_create_post_validation_error(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.post(
        "/api/posts",
        json={"title": ""},
        headers=headers,
    )
    assert response.status_code == 422
    assert "content" in response.text


@pytest.mark.anyio
async def test_create_post_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)
    
    post_data = {
        "title": "Test Post",
        "content": "Test content",
    }
    
    response = await client.post(
        "/api/posts",
        json=post_data,
        headers=headers
    )
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == post_data["title"]
    assert data["content"] == post_data["content"]
    assert data["user_id"] == user["id"]
    assert "id" in data
    assert "date_posted" in data
    assert data["author"]["username"] == "testuser"


@pytest.mark.anyio
async def test_create_post_unauthorized(client: AsyncClient):
    post_data = {
        "title": "Test Post",
        "content": "Test content",
    }
    
    response = await client.post(
        "/api/posts",
        json=post_data,
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_update_post_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.post(
        "/api/posts",
        json={"title": "Original Title", "content": "Original content"},
        headers=headers,
    )
    assert response.status_code == 201
    post_id = response.json()["id"]

    response = await client.patch(
        f"/api/posts/{post_id}",
        json={"title": "Updated Title"},
        headers=headers,
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Original content"


@pytest.mark.anyio
async def test_update_post_wrong_user(client: AsyncClient):
    await create_test_user(client, username="user1", email="user1@test.com")
    token1 = await login_user(client, email="user1@test.com")

    response = await client.post(
        "/api/posts",
        json={"title": "User 1's Post", "content": "Only user 1 can edit this"},
        headers=auth_header(token1),
    )
    assert response.status_code == 201
    post_id = response.json()["id"]

    await create_test_user(client, username="user2", email="user2@test.com")
    token2 = await login_user(client, email="user2@test.com")

    response = await client.patch(
        f"/api/posts/{post_id}",
        json={"title": "Hacked Title"},
        headers=auth_header(token2),
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to alter this post"


@pytest.mark.anyio
async def test_delete_post_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    create_response = await client.post(
        "/api/posts",
        json={"title": "Delete Me", "content": "Please delete this post."},
        headers=headers,
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/posts/{post_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/posts/{post_id}")
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_delete_post_wrong_user(client: AsyncClient):
    await create_test_user(client, username="user1", email="user1@test.com")
    token1 = await login_user(client, email="user1@test.com")

    create_response = await client.post(
        "/api/posts",
        json={"title": "User 1 Post", "content": "Owned by user 1."},
        headers=auth_header(token1),
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    await create_test_user(client, username="user2", email="user2@test.com")
    token2 = await login_user(client, email="user2@test.com")

    delete_response = await client.delete(
        f"/api/posts/{post_id}",
        headers=auth_header(token2),
    )
    assert delete_response.status_code == 403
    assert delete_response.json()["detail"] == "Not authorized to alter this post"


@pytest.mark.anyio
async def test_get_posts_with_pagination(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    for i in range(5):
        response = await client.post(
            "/api/posts",
            json={"title": f"Post {i}", "content": f"Content for post {i}"},
            headers=headers,
        )
        assert response.status_code == 201

    response = await client.get("/api/posts")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 5
    assert len(data["posts"]) == 5
    assert data["has_more"] is False

    response = await client.get("/api/posts?limit=2")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 5
    assert len(data["posts"]) == 2
    assert data["has_more"] is True

    response = await client.get("/api/posts?skip=2&limit=2")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 5
    assert len(data["posts"]) == 2
    assert data["skip"] == 2
    assert data["limit"] == 2
