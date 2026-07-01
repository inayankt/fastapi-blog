from typing import Annotated

from fastapi import APIRouter, Depends, status

from modules.users.dependencies import get_user_service
from modules.users.schemas import UserCreate, UserResponse, UserUpdate
from modules.users.service import UserService
from modules.posts.service import PostService
from modules.posts.schemas import PostResponse
from modules.posts.dependencies import get_post_service


router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.create_user(payload)


@router.get("/{user_id}", response_model=UserResponse)
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


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.update_user(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.delete_user(user_id)
