from modules.posts.exceptions import PostNotFoundError
from modules.posts.models import Post
from modules.posts.repository import PostRepository
from modules.posts.schemas import PostCreate, PostUpdate
from modules.users import User, UserNotFoundError, UserRepository


class PostService:
    def __init__(
        self, user_repository: UserRepository, post_repository: PostRepository
    ):
        self.user_repo = user_repository
        self.post_repo = post_repository

    async def list_posts(self) -> list[Post]:
        return await self.post_repo.get_all()

    async def get_post(self, post_id: int) -> Post:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise PostNotFoundError()
        return post

    async def get_posts_by_user(self, user_id: int) -> list[Post]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        posts = await self.post_repo.get_by_user_id(user_id)
        return user, posts

    async def create_post(self, user: User, payload: PostCreate) -> Post:
        new_post = await self.post_repo.create(
            title=payload.title,
            content=payload.content,
            user_id=user.id,
        )
        return new_post

    async def update_post(self, post: Post, payload: PostUpdate) -> Post:
        updated_post = await self.post_repo.update(
            post=post,
            title=payload.title,
            content=payload.content,
        )
        return updated_post

    async def delete_post(self, post: Post) -> None:
        await self.post_repo.delete(post)
