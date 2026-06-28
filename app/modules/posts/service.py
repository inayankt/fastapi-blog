from modules.posts.repository import PostRepository
from modules.posts.schemas import PostCreate, PostUpdate
from modules.posts.exceptions import PostNotFoundError
from modules.users.repository import UserRepository
from modules.users.exceptions import UserNotFoundError
from modules.posts.models import Post


class PostService:
    def __init__(
        self, user_repository: UserRepository, post_repository: PostRepository
    ):
        self.user_repo = user_repository
        self.post_repo = post_repository

    def list_posts(self) -> list[Post]:
        return self.post_repo.get_all()

    def get_post(self, post_id: int) -> Post:
        post = self.post_repo.get_by_id(post_id)
        if not post:
            raise PostNotFoundError()
        return post

    def get_posts_by_user(self, user_id: int) -> list[Post]:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        posts = self.post_repo.get_by_user_id(user_id)
        return user, posts

    def create_post(self, payload: PostCreate) -> Post:
        user = self.user_repo.get_by_id(payload.user_id)
        if not user:
            raise UserNotFoundError()

        new_post = self.post_repo.create(
            title=payload.title,
            content=payload.content,
            user_id=payload.user_id,
        )
        return new_post

    def update_post(self, post_id: int, payload: PostUpdate) -> Post:
        post = self.post_repo.get_by_id(post_id)
        if not post:
            raise PostNotFoundError()

        updated_post = self.post_repo.update(
            post=post,
            title=payload.title,
            content=payload.content,
        )
        return updated_post

    def delete_post(self, post_id: int) -> None:
        post = self.post_repo.get_by_id(post_id)
        if not post:
            raise PostNotFoundError()

        self.post_repo.delete(post)
