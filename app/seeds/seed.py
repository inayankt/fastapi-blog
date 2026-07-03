import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
from sqlalchemy import select, update

from db import AsyncSessionLocal, engine
from main import app
from modules.posts import Post
from seeds.reset import reset

IMAGES_DIR = Path(__file__).parent / "images"

users_file = Path(__file__).parent / "data" / "users.json"
posts_file = Path(__file__).parent / "data" / "posts.json"

with users_file.open("r", encoding="utf-8") as f:
    USERS = json.load(f)

with posts_file.open("r", encoding="utf-8") as f:
    POSTS = json.load(f)

# The 44th post - always the oldest (easter egg for pagination tutorial)
POST_44 = {
    "title": "Fun Fact: My High School Football Number Was #44",
    "content": "If you've paginated all the way to this post, the 44th one... you get to learn this fun fact: that my high school football number was #44. Other notable absolute legends who wore number #44 include: Jerry West (NBA - Also fellow WV Native), Hank Aaron (MLB), and Floyd Little (NFL).",
}


async def update_post_dates() -> None:
    now = datetime.now(UTC)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Post).order_by(Post.id))
        posts = result.scalars().all()

        if not posts:
            return

        # First post (POST_44) is the oldest - ~90 days ago
        await db.execute(
            update(Post)
            .where(Post.id == posts[0].id)
            .values(date_posted=now - timedelta(days=90)),
        )

        # Remaining posts: each ~1.5 days newer than previous
        for i, post in enumerate(posts[1:], start=1):
            days_ago = (len(posts) - i) * 1.5
            hours_offset = (i * 7) % 24
            post_date = now - timedelta(days=days_ago, hours=hours_offset)
            await db.execute(
                update(Post).where(Post.id == post.id).values(date_posted=post_date),
            )

        await db.commit()
    print("Updated post dates")


async def seed() -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://localhost",
    ) as client:
        await reset()

        users: list[dict] = []

        print(f"\nCreating {len(USERS)} users...")
        for user_data in USERS:
            response = await client.post(
                "/api/users",
                json={
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "password": user_data["password"],
                },
            )
            response.raise_for_status()
            user = response.json()
            print(f"\tCreated: {user['username']}")

            response = await client.post(
                "/api/auth/token",
                data={
                    "username": user_data["email"],
                    "password": user_data["password"],
                },
            )
            response.raise_for_status()
            token = response.json()["access_token"]

            if image_name := user_data.get("image"):
                image_path = IMAGES_DIR / image_name
                if image_path.exists():
                    response = await client.patch(
                        f"/api/users/{user['id']}/picture",
                        files={
                            "file": (
                                image_name,
                                image_path.read_bytes(),
                                "image/png",
                            ),
                        },
                        headers={"Authorization": f"Bearer {token}"},
                    )
                    response.raise_for_status()
                    print(f"\tUploaded: {image_name}")

            users.append(
                {"id": user["id"], "username": user["username"], "token": token}
            )

        print(f"\nCreating {len(POSTS) + 1} posts...")

        # First create POST_44 (will become oldest after date update)
        response = await client.post(
            "/api/posts",
            json={"title": POST_44["title"], "content": POST_44["content"]},
            headers={"Authorization": f"Bearer {users[0]['token']}"},
        )
        response.raise_for_status()
        print(f"\tCreated: '{POST_44['title']}'")

        # Create remaining posts in reverse (last in list = oldest, first = newest)
        for i, post_data in enumerate(reversed(POSTS)):
            user = users[i % len(users)]
            response = await client.post(
                "/api/posts",
                json={
                    "title": post_data["title"],
                    "content": post_data["content"],
                },
                headers={"Authorization": f"Bearer {user['token']}"},
            )
            response.raise_for_status()
            title = post_data["title"]
            print(
                f"  Created: '{title[:50]}...'"
                if len(title) > 50
                else f"\tCreated: '{title}'",
            )

        print("\nUpdating post dates...")
        await update_post_dates()

    await engine.dispose()

    print("\nDone!")
    print(f"\t{len(USERS)} users")
    print(f"\t{len(POSTS) + 1} posts")
    print("\tProfile pictures saved locally")


if __name__ == "__main__":
    asyncio.run(seed())
