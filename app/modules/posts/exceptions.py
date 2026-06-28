from core.exceptions import NotFoundError


class PostNotFoundError(NotFoundError):
    def __init__(self, detail: str = "Post not found"):
        super().__init__(detail)
