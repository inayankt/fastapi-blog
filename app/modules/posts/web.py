from typing import Annotated

from fastapi import APIRouter, Depends, Request

from core.templates import templates
from modules.posts.dependencies import get_post_service
from modules.posts.service import PostService


router = APIRouter()


@router.get("")
async def posts_page(
    request: Request,
    service: Annotated[PostService, Depends(get_post_service)],
):
    posts = await service.list_posts()
    return templates.TemplateResponse(
        request, "home.html", {"posts": posts, "title": "Home"}
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
