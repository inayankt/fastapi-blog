import asyncio

from sqlalchemy import delete

from core.storage import PROFILE_PICS_DIR
from db import AsyncSessionLocal
from modules.auth.models import PasswordResetToken
from modules.posts.models import Post
from modules.users.models import User


async def reset() -> None:
    # Delete profile pictures from local storage
    if PROFILE_PICS_DIR.exists():
        for file in PROFILE_PICS_DIR.iterdir():
            if file.is_file() and file.name != ".gitkeep":
                file.unlink()
        print(f"Deleted profile pictures from {PROFILE_PICS_DIR}")

    # Clear database tables (order respects foreign keys)
    async with AsyncSessionLocal() as db:
        await db.execute(delete(Post))
        await db.execute(delete(User))
        await db.execute(delete(PasswordResetToken))
        await db.commit()
    print("Cleared existing data")


if __name__ == "__main__":
    asyncio.run(reset())
