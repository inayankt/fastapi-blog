import pytest

from modules.posts.models import Post
from modules.posts.repository import PostRepository
from modules.users.repository import UserRepository


@pytest.fixture
def repo(db_session):
    return PostRepository(db_session)


@pytest.fixture
async def users(db_session):
    user_repo = UserRepository(db_session)
    users = []
    users.append(
        await user_repo.create(
            username="test-1",
            email="test-1@test.com",
            password_hash="hash1",
        )
    )
    users.append(
        await user_repo.create(
            username="test-2",
            email="test-2@test.com",
            password_hash="hash2",
        )
    )
    return users


@pytest.fixture
async def populated_posts(repo, users):
    created_posts = []
    created_posts.append(await repo.create(title="t1", content="c1", user_id=users[0].id))
    created_posts.append(await repo.create(title="t2", content="c2", user_id=users[0].id))
    created_posts.append(await repo.create(title="t3", content="c3", user_id=users[1].id))
    return created_posts


@pytest.mark.anyio
async def test_count_all_empty(repo):
    count = await repo.count_all()

    assert count == 0


@pytest.mark.anyio
async def test_get_all_empty(repo):
    posts = await repo.get_all()

    assert posts == []


@pytest.mark.anyio
async def test_create(repo, users):
    created = await repo.create(title="t", content="c", user_id=users[0].id)

    assert isinstance(created, Post)
    assert created.title == "t"
    assert created.content == "c"
    assert created.user_id == users[0].id


@pytest.mark.anyio
async def test_count_all(repo, populated_posts):
    count = await repo.count_all()

    assert count == 3


@pytest.mark.anyio
async def test_count_by_user(repo, users, populated_posts):
    count_1 = await repo.count_by_user(users[0].id)
    count_2 = await repo.count_by_user(users[1].id)
    count_3 = await repo.count_by_user(9999)

    assert count_1 == 2
    assert count_2 == 1
    assert count_3 == 0


@pytest.mark.anyio
async def test_get_all(repo, populated_posts):
    posts = await repo.get_all()

    assert len(posts) == len(populated_posts)
    assert all(isinstance(post, Post) for post in posts)
    assert [p.id for p in posts] == [p.id for p in populated_posts[::-1]]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "skip, limit",
    [
        (0, 1),
        (1, 1),
        (1, 2),
        (2, 5),
        (4, 1),
    ],
)
async def test_get_all_with_skip_limit(repo, populated_posts, skip, limit):
    posts = await repo.get_all(skip=skip, limit=limit)

    assert len(posts) == min(limit, max(0, len(populated_posts) - skip))
    assert all(isinstance(post, Post) for post in posts)
    assert [p.id for p in posts] == [p.id for p in populated_posts[::-1][skip : skip + limit]]


@pytest.mark.anyio
async def test_get_by_id(repo, populated_posts):
    post = await repo.get_by_id(populated_posts[0].id)

    assert post is not None
    assert isinstance(post, Post)
    assert post.id == populated_posts[0].id
    assert post.title == populated_posts[0].title
    assert post.user_id == populated_posts[0].user_id
    assert post.author.username == populated_posts[0].author.username


@pytest.mark.anyio
async def test_get_by_user_id_empty(repo, users):
    posts = await repo.get_by_user_id(users[0].id)

    assert posts == []


@pytest.mark.anyio
async def test_get_by_user_id(repo, users, populated_posts):
    posts_1 = await repo.get_by_user_id(users[0].id)
    posts_2 = await repo.get_by_user_id(users[1].id)
    posts_3 = await repo.get_by_user_id(999)

    user_1_posts = [p for p in populated_posts if p.user_id == users[0].id]
    user_2_posts = [p for p in populated_posts if p.user_id == users[1].id]

    assert len(posts_1) == len(user_1_posts)
    assert all(isinstance(post, Post) for post in posts_1)
    assert [p.id for p in posts_1] == [p.id for p in user_1_posts[::-1]]

    assert len(posts_2) == len(user_2_posts)
    assert all(isinstance(post, Post) for post in posts_2)
    assert [p.id for p in posts_2] == [p.id for p in user_2_posts[::-1]]

    assert posts_3 == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    "skip, limit",
    [
        (0, 1),
        (1, 1),
        (1, 5),
        (3, 1),
    ],
)
async def test_get_by_user_id_with_skip_limit(repo, users, populated_posts, skip, limit):
    posts = await repo.get_by_user_id(user_id=users[0].id, skip=skip, limit=limit)

    user_1_posts = [p for p in populated_posts if p.user_id == users[0].id]

    assert len(posts) == min(limit, max(0, len(user_1_posts) - skip))
    assert all(isinstance(post, Post) for post in posts)
    assert [p.id for p in posts] == [p.id for p in user_1_posts[::-1][skip : skip + limit]]


@pytest.mark.anyio
async def test_update(repo, populated_posts):
    updated = await repo.update(
        post=populated_posts[0],
        title="updated-title",
        content="updated-content",
    )

    assert updated.title == "updated-title"
    assert updated.content == "updated-content"
    assert updated.id == populated_posts[0].id


@pytest.mark.anyio
async def test_delete(repo, populated_posts):
    await repo.delete(populated_posts[0])

    remaining_posts = await repo.get_all()
    deleted_post = await repo.get_by_id(populated_posts[0].id)

    assert len(remaining_posts) == 2
    assert deleted_post is None
