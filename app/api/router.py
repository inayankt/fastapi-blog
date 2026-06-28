from fastapi import APIRouter

from modules.users.api import router as users_router
from modules.posts.api import router as posts_router

router = APIRouter(prefix="/api")

router.include_router(users_router)
router.include_router(posts_router)
