from typing import Annotated

from fastapi import APIRouter, Depends, status

from modules.posts.dependencies import get_post_service
from modules.posts.service import PostService
from modules.posts.schemas import PostResponse
from modules.users.dependencies import get_user_service
from modules.users.schemas import UserCreate, UserResponse
from modules.users.service import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return service.create_user(payload)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return service.get_user(user_id)


@router.get("/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(
    user_id: int,
    service: PostService = Depends(get_post_service),
):
    _, posts = service.get_posts_by_user(user_id)
    return posts
