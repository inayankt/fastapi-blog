from modules.posts.repository import PostRepository
from modules.posts.schemas import PostCreate
from modules.posts.exceptions import PostNotFoundError
from modules.users.repository import UserRepository
from modules.users.exceptions import UserNotFoundError


class PostService:
    def __init__(self, user_repository: UserRepository, post_repository: PostRepository):
        self.repo = {"user": user_repository, "post": post_repository}

    def list_posts(self):
        return self.repo["post"].get_all()

    def get_post(self, post_id: int):
        post = self.repo["post"].get_by_id(post_id)
        if not post:
            raise PostNotFoundError()
        return post

    def get_posts_by_user(self, user_id: int):
        user = self.repo["user"].get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        posts = self.repo["post"].get_by_user_id(user_id)
        return user, posts

    def create_post(self, payload: PostCreate):
        user = self.repo["user"].get_by_id(payload.user_id)
        if not user:
            raise UserNotFoundError()

        new_post = self.repo["post"].create(
            title=payload.title,
            content=payload.content,
            user_id=payload.user_id,
        )
        return new_post
