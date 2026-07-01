from typing import Annotated

from fastapi import APIRouter, Depends, status

from modules.posts.dependencies import get_post_service
from modules.posts.schemas import PostCreate, PostResponse, PostUpdate
from modules.posts.service import PostService


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
    service: Annotated[PostService, Depends(get_post_service)],
):
    return await service.create_post(payload)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    payload: PostUpdate,
    service: Annotated[PostService, Depends(get_post_service)],
):
    return await service.update_post(post_id, payload)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    service: Annotated[PostService, Depends(get_post_service)],
):
    return await service.delete_post(post_id)
