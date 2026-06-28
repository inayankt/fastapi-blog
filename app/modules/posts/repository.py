from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.posts.models import Post


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Post]:
        result = self.db.execute(
            select(Post)
        )
        return list(result.scalars().all())

    def get_by_id(self, post_id: int) -> Post | None:
        result = self.db.execute(
            select(Post).where(Post.id == post_id)
        )
        return result.scalars().first()

    def get_by_user_id(self, user_id: int) -> list[Post]:
        result = self.db.execute(
            select(Post).where(Post.user_id == user_id)
        )
        return list(result.scalars().all())

    def create(self, title: str, content: str, user_id: int) -> Post:
        new_post = Post(title=title, content=content, user_id=user_id)
        self.db.add(new_post)
        self.db.commit()
        self.db.refresh(new_post)
        return new_post
