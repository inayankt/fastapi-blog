from fastapi import APIRouter

from modules.auth.api import router as auth_router
from modules.posts.api import router as posts_router
from modules.users.api import router as users_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(posts_router, prefix="/posts", tags=["posts"])
