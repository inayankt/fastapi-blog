from typing import Annotated

from fastapi import APIRouter, Depends, status

from modules.auth.dependencies import get_current_user, is_post_owner
from modules.posts.dependencies import get_post_service
from modules.posts.models import Post
from modules.posts.schemas import PostCreate, PostResponse, PostUpdate
from modules.posts.service import PostService
from modules.users.models import User

router = APIRouter()


@router.get("", response_model=list[PostResponse])
async def get_posts(
    service: Annotated[PostService, Depends(get_post_service)],
):
    return await service.list_posts()


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    service: Annotated[PostService, Depends(get_post_service)],
):
    return await service.get_post(post_id)


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[PostService, Depends(get_post_service)],
):
    return await service.create_post(current_user, payload)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    payload: PostUpdate,
    post: Annotated[Post, Depends(is_post_owner)],
    service: Annotated[PostService, Depends(get_post_service)],
):
    return await service.update_post(post, payload)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post: Annotated[Post, Depends(is_post_owner)],
    service: Annotated[PostService, Depends(get_post_service)],
):
    return await service.delete_post(post)
