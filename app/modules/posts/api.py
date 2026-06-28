from typing import Annotated

from fastapi import APIRouter, Depends, status

from modules.posts.dependencies import get_post_service
from modules.posts.schemas import PostCreate, PostResponse
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


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    service: Annotated[PostService, Depends(get_post_service)],
):
    return service.create_post(payload)
