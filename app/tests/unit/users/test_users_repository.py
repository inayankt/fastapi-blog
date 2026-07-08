import pytest

from core.config import settings
from modules.users.models import User
from modules.users.repository import UserRepository


@pytest.fixture
def repo(db_session):
    return UserRepository(db_session)


@pytest.fixture
async def users(repo):
    created_users = []
    created_users.append(
        await repo.create(
            username="test-1",
            email="test-1@test.com",
            password_hash="hash1",
        )
    )
    created_users.append(
        await repo.create(
            username="test-2",
            email="test-2@test.com",
            password_hash="hash2",
        )
    )
    return created_users


@pytest.mark.anyio
async def test_create(repo):
    created = await repo.create(
        username="new-user",
        email="new-user@test.com",
        password_hash="hash",
    )

    assert isinstance(created, User)
    assert created.username == "new-user"
    assert created.email == "new-user@test.com"
    assert created.password_hash == "hash"
    assert created.image_file is None
    assert created.image_path == "/static/profile_pics/default.jpg"


@pytest.mark.anyio
async def test_get_by_id(repo, users):
    user = await repo.get_by_id(users[0].id)

    assert user is not None
    assert isinstance(user, User)
    assert user.id == users[0].id
    assert user.username == users[0].username
    assert user.email == users[0].email


@pytest.mark.anyio
async def test_get_by_username(repo, users):
    user = await repo.get_by_username(users[0].username)
    missing_user = await repo.get_by_username("does-not-exist")

    assert user is not None
    assert isinstance(user, User)
    assert user.id == users[0].id
    assert missing_user is None


@pytest.mark.anyio
async def test_get_by_email(repo, users):
    user = await repo.get_by_email(users[1].email)
    missing_user = await repo.get_by_email("missing@test.com")

    assert user is not None
    assert isinstance(user, User)
    assert user.id == users[1].id
    assert missing_user is None


@pytest.mark.anyio
async def test_update_details(repo, users):
    updated = await repo.update_details(
        user=users[0],
        username="updated-name",
        email="updated@test.com",
    )

    assert updated.id == users[0].id
    assert updated.username == "updated-name"
    assert updated.email == "updated@test.com"


@pytest.mark.anyio
async def test_update_image(repo, users):
    updated = await repo.update_image(user=users[0], image_file="avatar.jpg")

    assert updated.id == users[0].id
    assert updated.image_file == "avatar.jpg"
    assert updated.image_path == f"https://{settings.s3_bucket_name}.s3.{settings.s3_region}.amazonaws.com/{settings.s3_bucket_prefix}/avatar.jpg"
    
    updated = await repo.update_image(user=users[0])
    
    assert updated.id == users[0].id
    assert updated.image_file is None
    assert updated.image_path == "/static/profile_pics/default.jpg"


@pytest.mark.anyio
async def test_update_password(repo, users):
    updated = await repo.update_password(user=users[0], new_password_hash="new-hash")

    assert updated.id == users[0].id
    assert updated.password_hash == "new-hash"


@pytest.mark.anyio
async def test_delete(repo, users):
    await repo.delete(users[0])

    deleted_user = await repo.get_by_id(users[0].id)
    remaining_user = await repo.get_by_id(users[1].id)

    assert deleted_user is None
    assert remaining_user is not None
