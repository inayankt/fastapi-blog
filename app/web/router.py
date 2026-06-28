from typing import Annotated

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from core.templates import templates
from modules.users.web import router as users_router
from modules.posts.web import router as posts_router
from modules.posts.service import PostService
from modules.posts.dependencies import get_post_service


router = APIRouter()

@router.get("/", include_in_schema=False)
def home_page(
    request: Request,
    service: Annotated[PostService, Depends(get_post_service)],
):
    posts = service.list_posts()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"}
    )

router.include_router(users_router)
router.include_router(posts_router)
