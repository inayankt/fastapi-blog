import subprocess

from sqlalchemy import text

from db import AsyncSessionLocal


async def reset_database() -> None:
    print("\nDropping database schema...")

    async with AsyncSessionLocal() as db:
        await db.execute(text("DROP SCHEMA public CASCADE"))
        await db.execute(text("CREATE SCHEMA public"))
        await db.commit()

    print("\nRunning Alembic migrations...")

    subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        check=True,
    )

    print("\nDatabase ready.")
