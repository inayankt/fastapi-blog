import pytest

from modules.auth.models import PasswordResetToken
from modules.auth.repository import AuthRepository
from modules.users.repository import UserRepository


@pytest.fixture
def repo(db_session):
    return AuthRepository(db_session)


@pytest.fixture
async def user(db_session):
    user_repo = UserRepository(db_session)
    return await user_repo.create(
        username="auth-user",
        email="auth-user@test.com",
        password_hash="hash1",
    )


@pytest.fixture
async def reset_tokens(repo, user):
    created_tokens = []
    created_tokens.append(
        await repo.create(
            user_id=user.id,
            token_hash="token-hash-1",
            expires_at="2030-01-01T00:00:00",
        )
    )
    created_tokens.append(
        await repo.create(
            user_id=user.id,
            token_hash="token-hash-2",
            expires_at="2030-01-02T00:00:00",
        )
    )
    return created_tokens


@pytest.mark.anyio
async def test_create(repo, user):
    created = await repo.create(
        user_id=user.id,
        token_hash="token-create",
        expires_at="2030-01-03T00:00:00",
    )

    assert isinstance(created, PasswordResetToken)
    assert created.user_id == user.id
    assert created.token_hash == "token-create"
    assert created.expires_at == "2030-01-03T00:00:00"


@pytest.mark.anyio
async def test_get_by_token_hash(repo, reset_tokens):
    token = await repo.get_by_token_hash(reset_tokens[0].token_hash)
    missing_token = await repo.get_by_token_hash("does-not-exist")

    assert token is not None
    assert isinstance(token, PasswordResetToken)
    assert token.token_hash == reset_tokens[0].token_hash
    assert missing_token is None


@pytest.mark.anyio
async def test_delete(repo, reset_tokens):
    await repo.delete(reset_tokens[0])

    deleted_token = await repo.get_by_token_hash(reset_tokens[0].token_hash)
    remaining_token = await repo.get_by_token_hash(reset_tokens[1].token_hash)

    assert deleted_token is None
    assert remaining_token is not None


@pytest.mark.anyio
async def test_delete_by_user_id(repo, user, reset_tokens):
    await repo.delete_by_user_id(user.id)

    token_1 = await repo.get_by_token_hash(reset_tokens[0].token_hash)
    token_2 = await repo.get_by_token_hash(reset_tokens[1].token_hash)

    assert token_1 is None
    assert token_2 is None
