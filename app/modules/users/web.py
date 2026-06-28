from typing import Annotated

from fastapi import APIRouter, Depends, Request

from core.templates import templates
from modules.posts.dependencies import get_post_service
from modules.users.dependencies import get_user_service
from modules.posts.service import PostService
from modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["posts"])


@router.get("/{user_id}/posts", include_in_schema=False)
def user_posts_page(
    request: Request,
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
    post_service: Annotated[PostService, Depends(get_post_service)],
):
    user, posts = post_service.get_posts_by_user(user_id)
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )
