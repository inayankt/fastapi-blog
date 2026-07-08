from modules.posts.exceptions import PostNotFoundError
from modules.posts.models import Post
from modules.posts.repository import PostRepository
from modules.users.models import User


class PostService:
    def __init__(self, repository: PostRepository):
        self.repo = repository

    async def get_posts(self, skip: int = 0, limit: int = 100) -> dict:
        total = await self.repo.count_all()
        posts = await self.repo.get_all(skip, limit)
        has_more = skip + len(posts) < total
        return {
            "posts": posts,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": has_more,
        }

    async def get_post(self, post_id: int) -> Post:
        post = await self.repo.get_by_id(post_id)
        if not post:
            raise PostNotFoundError()
        return post

    async def create_post(self, user: User, title: str, content: str) -> Post:
        new_post = await self.repo.create(
            title=title,
            content=content,
            user_id=user.id,
        )
        return new_post

    async def update_post(self, post: Post, title: str, content: str) -> Post:
        updated_post = await self.repo.update(
            post=post,
            title=title,
            content=content,
        )
        return updated_post

    async def delete_post(self, post: Post) -> None:
        await self.repo.delete(post)
