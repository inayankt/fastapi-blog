from typing import Annotated

from fastapi import APIRouter, Depends, status, UploadFile

from modules.auth import is_valid_current_user
from modules.posts import (
    PostResponse,
    PostService,
    get_post_service,
)
from modules.users.dependencies import get_user_service
from modules.users.models import User
from modules.users.schemas import UserCreate, UserPrivate, UserPublic, UserUpdate
from modules.users.service import UserService

router = APIRouter()


@router.post("", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.create_user(payload)


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.get_user(user_id)


@router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(
    user_id: int,
    service: Annotated[PostService, Depends(get_post_service)],
):
    _, posts = await service.get_posts_by_user(user_id)
    return posts


@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user(
    payload: UserUpdate,
    user: Annotated[User, Depends(is_valid_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.update_user(user, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user: Annotated[User, Depends(is_valid_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.delete_user(user)


@router.patch("/{user_id}/picture", response_model=UserPrivate)
async def upload_profile_picture(
    file: UploadFile,
    user: Annotated[User, Depends(is_valid_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.upload_profile_picture(user, file)


@router.delete("/{user_id}/picture", response_model=UserPrivate)
async def delete_profile_picture(
    user: Annotated[User, Depends(is_valid_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.delete_profile_picture(user)
