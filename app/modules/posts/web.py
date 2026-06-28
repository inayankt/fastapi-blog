from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from modules.posts.dependencies import get_post_service
from modules.posts.service import PostService


router = APIRouter(prefix="/posts", tags=["posts"])

templates = Jinja2Templates(directory="templates")


@router.get("/", include_in_schema=False)
def posts_page(
    request: Request,
    service: Annotated[PostService, Depends(get_post_service)],
):
    posts = service.list_posts()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"}
    )

@router.get("/{post_id}", include_in_schema=False)
def post_page(
    request: Request,
    post_id: int,
    service: Annotated[PostService, Depends(get_post_service)],
):
    post = service.get_post(post_id)
    return templates.TemplateResponse(
        request,
        "post.html",
        {"post": post, "title": post.title[:50]},
    )
