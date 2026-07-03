import asyncio

from sqlalchemy import delete

from db import AsyncSessionLocal
from core.storage import PROFILE_PICS_DIR
from modules.users import User
from modules.posts import Post


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
        await db.commit()
    print("Cleared existing data")


if __name__ == "__main__":
    asyncio.run(reset())
    