from typing import Annotated

from fastapi import APIRouter, Depends, Request

from core.config import settings
from core.templates import templates
from modules.posts.dependencies import get_post_service
from modules.posts.service import PostService

router = APIRouter()


@router.get("")
async def posts_page(
    request: Request,
    service: Annotated[PostService, Depends(get_post_service)],
):
    paginated_posts = await service.get_posts(skip=0, limit=settings.posts_per_page)
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": paginated_posts["posts"],
            "title": "Home",
            "limit": settings.posts_per_page,
            "has_more": paginated_posts["has_more"],
        },
    )


@router.get("/{post_id}")
async def post_page(
    request: Request,
    post_id: int,
    service: Annotated[PostService, Depends(get_post_service)],
):
    post = await service.get_post(post_id)
    return templates.TemplateResponse(
        request,
        "post.html",
        {"post": post, "title": post.title[:50]},
    )
