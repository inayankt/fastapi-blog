from typing import Annotated

from fastapi import APIRouter, Depends, Request

from core.templates import templates
from modules.posts.dependencies import get_post_service
from modules.posts.service import PostService
from modules.posts.web import router as posts_router
from modules.users.web import router as users_router

router = APIRouter()


@router.get("/")
async def home_page(
    request: Request,
    service: Annotated[PostService, Depends(get_post_service)],
):
    posts = await service.list_posts()
    return templates.TemplateResponse(
        request, "home.html", {"posts": posts, "title": "Home"}
    )


router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(posts_router, prefix="/posts", tags=["posts"])
