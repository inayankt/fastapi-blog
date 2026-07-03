from typing import Annotated

from fastapi import APIRouter, Depends, Request

from core.config import settings
from core.templates import templates
from modules.users.dependencies import get_user_service
from modules.users.service import UserService

router = APIRouter()


@router.get("/{user_id}/posts")
async def user_posts_page(
    request: Request,
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
):
    user, paginated_posts = await service.get_posts_by_user(
        user_id=user_id, skip=0, limit=settings.posts_per_page
    )
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts": paginated_posts["posts"],
            "user": user,
            "title": f"{user.username}'s Posts",
            "limit": settings.posts_per_page,
            "has_more": paginated_posts["has_more"],
        },
    )
