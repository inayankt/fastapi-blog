from fastapi import APIRouter

from modules.users.api import router as users_router
from modules.posts.api import router as posts_router

router = APIRouter()

router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(posts_router, prefix="/posts", tags=["posts"])
