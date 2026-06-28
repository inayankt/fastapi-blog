from typing import Annotated

from fastapi import APIRouter, Depends, status

from modules.posts.dependencies import get_post_service
from modules.posts.schemas import PostCreate, PostResponse, PostUpdate
from modules.posts.service import PostService


router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[PostResponse])
def get_posts(
    service: Annotated[PostService, Depends(get_post_service)],
):
    return service.list_posts()


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    service: Annotated[PostService, Depends(get_post_service)],
):
    return service.get_post(post_id)


@router.get("/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(
    user_id: int,
    service: Annotated[PostService, Depends(get_post_service)],
):
    _, posts = service.get_posts_by_user(user_id)
    return posts


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    service: Annotated[PostService, Depends(get_post_service)],
):
    return service.create_post(payload)


@router.patch("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    payload: PostUpdate,
    service: Annotated[PostService, Depends(get_post_service)],
):
    return service.update_post(post_id, payload)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    service: Annotated[PostService, Depends(get_post_service)],
):
    return service.delete_post(post_id)
