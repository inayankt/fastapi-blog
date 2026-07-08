from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest
from botocore.exceptions import ClientError
from fastapi import UploadFile
from PIL import UnidentifiedImageError

from core.config import settings
from modules.users.exceptions import (
    EmailAlreadyExistsError,
    FileTooLargeError,
    ImageUploadError,
    InvalidImageError,
    NoProfilePictureError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from modules.users.models import User
from modules.users.service import UserService


@pytest.fixture
def repos_and_svc():
    user_repo = AsyncMock()
    post_repo = AsyncMock()
    svc = UserService(user_repository=user_repo, post_repository=post_repo)
    return user_repo, post_repo, svc


@pytest.mark.anyio
async def test_get_user(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user = User(id=1, username="test", email="test@test.com", password_hash="hash")
    user_repo.get_by_id.return_value = user

    result = await svc.get_user(user_id=1)

    assert result == user
    user_repo.get_by_id.assert_awaited_once_with(1)


@pytest.mark.anyio
async def test_get_user_not_found(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user_repo.get_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        await svc.get_user(user_id=1)


@pytest.mark.anyio
async def test_create_user(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user_repo.get_by_username.return_value = None
    user_repo.get_by_email.return_value = None
    user_repo.create.return_value = User(
        id=1,
        username="new-user",
        email="new@test.com",
        password_hash="hash",
    )

    result = await svc.create_user(username="new-user", email="new@test.com", password="password")

    assert result.username == "new-user"
    assert result.email == "new@test.com"
    user_repo.get_by_username.assert_awaited_once_with("new-user")
    user_repo.get_by_email.assert_awaited_once_with("new@test.com")
    user_repo.create.assert_awaited_once()


@pytest.mark.anyio
async def test_create_user_username_exists(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user_repo.get_by_username.return_value = User(
        id=1,
        username="new-user",
        email="old@test.com",
        password_hash="hash",
    )

    with pytest.raises(UsernameAlreadyExistsError):
        await svc.create_user(username="new-user", email="new@test.com", password="password")
    
    user_repo.create.assert_not_awaited()


@pytest.mark.anyio
async def test_create_user_email_exists(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user_repo.get_by_username.return_value = None
    user_repo.get_by_email.return_value = User(
        id=1,
        username="other",
        email="new@test.com",
        password_hash="hash",
    )

    with pytest.raises(EmailAlreadyExistsError):
        await svc.create_user(username="new-user", email="new@test.com", password="password")
    
    user_repo.create.assert_not_awaited()


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
async def test_get_posts_by_user(repos_and_svc, skip, limit, posts):
    user_repo, post_repo, svc = repos_and_svc
    user = User(id=1, username="test", email="test@test.com", password_hash="hash")
    user_repo.get_by_id.return_value = user
    post_repo.count_by_user.return_value = 3
    post_repo.get_by_user_id.return_value = posts

    returned_user, result = await svc.get_posts_by_user(user_id=1, skip=skip, limit=limit)

    assert returned_user == user
    assert result["total"] == 3
    assert result["skip"] == skip
    assert result["limit"] == limit
    assert result["posts"] == posts
    assert result["has_more"] is (skip + limit < 3)


@pytest.mark.anyio
async def test_update_user_success(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user = User(id=1, username="old", email="old@test.com", password_hash="hash")
    user_repo.get_by_username.return_value = None
    user_repo.get_by_email.return_value = None
    user_repo.update_details.return_value = User(
        id=1,
        username="new",
        email="new@test.com",
        password_hash="hash",
    )

    result = await svc.update_user(user=user, username="new", email="new@test.com")

    assert result.username == "new"
    assert result.email == "new@test.com"
    user_repo.update_details.assert_awaited_once()


@pytest.mark.anyio
async def test_update_user_username_exists(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user = User(id=1, username="old", email="old@test.com", password_hash="hash")
    user_repo.get_by_username.return_value = User(
        id=2,
        username="taken",
        email="other@test.com",
        password_hash="hash",
    )

    with pytest.raises(UsernameAlreadyExistsError):
        await svc.update_user(user=user, username="taken", email=None)
    
    user_repo.update_details.assert_not_awaited()
        

@pytest.mark.anyio
async def test_update_user_email_exists(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user = User(id=1, username="old", email="old@test.com", password_hash="hash")
    user_repo.get_by_username.return_value = User(
        id=2,
        username="other",
        email="taken@test.com",
        password_hash="hash",
    )

    with pytest.raises(EmailAlreadyExistsError):
        await svc.update_user(user=user, username=None, email="taken@test.com")
    
    user_repo.update_details.assert_not_awaited()


@pytest.mark.anyio
async def test_delete_user(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user = User(
        id=1,
        username="test",
        email="test@test.com",
        password_hash="hash",
        image_file="avatar.jpg",
    )
        
    with patch(
        "modules.users.service.delete_profile_image",
        new_callable=AsyncMock,
    ) as mock_delete:
        await svc.delete_user(user)
        mock_delete.assert_awaited_once_with(user.image_file)

    user_repo.delete.assert_awaited_once_with(user)


@pytest.mark.anyio
async def test_upload_profile_picture_file_too_large(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user = User(id=1, username="test", email="test@test.com", password_hash="hash")
    file = UploadFile(
        filename="a.jpg",
        file=BytesIO(b"a" * (settings.max_upload_size_bytes + 1)),
    )

    with pytest.raises(FileTooLargeError):
        await svc.upload_profile_picture(user=user, file=file)
    
    user_repo.update_image.assert_not_awaited()


@pytest.mark.anyio
async def test_upload_profile_picture_invalid_image(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user = User(id=1, username="test", email="test@test.com", password_hash="hash")
    file = UploadFile(filename="a.jpg", file=BytesIO(b"abc"))
    
    with patch(
        "modules.users.service.run_in_threadpool",
        new_callable=AsyncMock,
    ) as mock_run_in_threadpool:
        mock_run_in_threadpool.side_effect = UnidentifiedImageError("bad image")
        
        with pytest.raises(InvalidImageError):
            await svc.upload_profile_picture(user=user, file=file)
        
        mock_run_in_threadpool.assert_awaited_once()
        user_repo.update_image.assert_not_awaited()


@pytest.mark.anyio
async def test_upload_profile_picture_upload_error(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user = User(id=1, username="test", email="test@test.com", password_hash="hash")
    file = UploadFile(filename="a.jpg", file=BytesIO(b"abc"))
    
    with (
        patch(
            "modules.users.service.run_in_threadpool",
            new_callable=AsyncMock,
        ) as mock_run_in_threadpool,
        patch(
            "modules.users.service.upload_profile_image",
            new_callable=AsyncMock,
        ) as mock_upload,
    ):
        mock_run_in_threadpool.return_value = (b"img", "avatar.jpg")
        mock_upload.side_effect = ClientError(
            {"Error": {"Code": "Test", "Message": "boom"}},
            "PutObject",
        )

        with pytest.raises(ImageUploadError):
            await svc.upload_profile_picture(user=user, file=file)

        mock_run_in_threadpool.assert_awaited_once()
        mock_upload.assert_awaited_once()
        user_repo.update_image.assert_not_awaited()


@pytest.mark.anyio
async def test_delete_profile_picture(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user = User(
        id=1,
        username="test",
        email="test@test.com",
        password_hash="hash",
        image_file="avatar.jpg",
    )
    user_repo.update_image.return_value = user
        
    with patch(
        "modules.users.service.delete_profile_image",
        new_callable=AsyncMock,
    ) as mock_delete:
        result = await svc.delete_profile_picture(user=user)
        mock_delete.assert_awaited_once_with(user.image_file)

    assert result == user
    user_repo.update_image.assert_awaited_once_with(user, None)


@pytest.mark.anyio
async def test_delete_profile_picture_no_image(repos_and_svc):
    user_repo, _, svc = repos_and_svc
    user = User(id=1, username="test", email="test@test.com", password_hash="hash")

    with pytest.raises(NoProfilePictureError):
        await svc.delete_profile_picture(user=user)
    
    user_repo.update_image.assert_not_awaited()
