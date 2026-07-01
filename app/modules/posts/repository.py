from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.posts.models import Post


class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Post]:
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.author))
            .order_by(Post.date_posted.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, post_id: int) -> Post | None:
        result = await self.db.execute(
            select(Post).options(selectinload(Post.author)).where(Post.id == post_id)
        )
        return result.scalars().first()

    async def get_by_user_id(self, user_id: int) -> list[Post]:
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.author))
            .where(Post.user_id == user_id)
            .order_by(Post.date_posted.desc())
        )
        return list(result.scalars().all())

    async def create(self, title: str, content: str, user_id: int) -> Post:
        new_post = Post(title=title, content=content, user_id=user_id)
        self.db.add(new_post)
        await self.db.commit()
        await self.db.refresh(new_post, attribute_names=["author"])
        return new_post

    async def update(
        self,
        post: Post,
        title: str | None = None,
        content: str | None = None,
    ) -> Post:
        if title is not None:
            post.title = title
        if content is not None:
            post.content = content
        await self.db.commit()
        await self.db.refresh(post, attribute_names=["author"])
        return post

    async def delete(self, post: Post) -> None:
        await self.db.delete(post)
        await self.db.commit()
