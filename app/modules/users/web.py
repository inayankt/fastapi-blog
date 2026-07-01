from typing import Annotated

from fastapi import APIRouter, Depends, Request

from core.templates import templates
from modules.posts.dependencies import get_post_service
from modules.posts.service import PostService

router = APIRouter()


@router.get("/{user_id}/posts")
async def user_posts_page(
    request: Request,
    user_id: int,
    service: Annotated[PostService, Depends(get_post_service)],
):
    user, posts = await service.get_posts_by_user(user_id)
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )
