from unittest.mock import AsyncMock

import pytest

from modules.posts.exceptions import PostNotFoundError
from modules.posts.models import Post
from modules.posts.service import PostService


@pytest.fixture
def repo_and_svc():
    repo = AsyncMock()
    svc = PostService(repository=repo)
    return repo, svc


@pytest.mark.anyio
@pytest.mark.parametrize(
    "skip, limit, posts",
    [
        (0, 2, ["p1", "p2"]),
        (1, 1, ["p2"]),
        (1, 2, ["p2", "p3"]),
        (2, 5, ["p3"]),
        (4, 1, []),
    ],
)
async def test_get_posts_pagination(repo_and_svc, skip, limit, posts):
    repo, svc = repo_and_svc
    repo.count_all.return_value = 3
    repo.get_all.return_value = posts

    res = await svc.get_posts(skip=skip, limit=limit)

    assert res["total"] == 3
    assert res["skip"] == skip
    assert res["limit"] == limit
    assert res["posts"] == posts
    assert res["has_more"] is (skip + limit < 3)


@pytest.mark.anyio
async def test_get_post(repo_and_svc):
    repo, svc = repo_and_svc
    post = Post(id=1, title="t", content="c", user_id=1)
    repo.get_by_id.return_value = post

    result = await svc.get_post(post_id=1)

    assert result == post
    repo.get_by_id.assert_awaited_once_with(1)


@pytest.mark.anyio
async def test_get_post_not_found(repo_and_svc):
    repo, svc = repo_and_svc
    repo.get_by_id.return_value = None

    with pytest.raises(PostNotFoundError):
        await svc.get_post(post_id=1)


@pytest.mark.anyio
async def test_create_post(repo_and_svc):
    repo, svc = repo_and_svc
    user = type("User", (), {"id": 1})()
    post = Post(id=1, title="t", content="c", user_id=1)
    repo.create.return_value = post

    result = await svc.create_post(user=user, title="t", content="c")

    assert result == post
    repo.create.assert_awaited_once_with(title="t", content="c", user_id=1)


@pytest.mark.anyio
async def test_update_post(repo_and_svc):
    repo, svc = repo_and_svc
    post = Post(id=1, title="old", content="old", user_id=1)
    updated_post = Post(id=1, title="new", content="new", user_id=1)
    repo.update.return_value = updated_post

    result = await svc.update_post(post=post, title="new", content="new")

    assert result == updated_post
    repo.update.assert_awaited_once_with(post=post, title="new", content="new")


@pytest.mark.anyio
async def test_delete_post(repo_and_svc):
    repo, svc = repo_and_svc
    post = Post(id=1, title="t", content="c", user_id=1)

    await svc.delete_post(post)

    repo.delete.assert_awaited_once_with(post)
