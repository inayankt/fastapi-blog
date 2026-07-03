from typing import Annotated

from fastapi import APIRouter, Depends, Request

from core.config import settings
from core.templates import templates
from modules.auth.web import router as auth_router
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


router.include_router(users_router, prefix="/users")
router.include_router(posts_router, prefix="/posts")
router.include_router(auth_router)
