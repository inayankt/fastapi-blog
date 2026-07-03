from core.exceptions import ConflictError, NotFoundError, BadRequestError
from core.config import settings


class UserNotFoundError(NotFoundError):
    def __init__(self, detail: str = "User not found"):
        super().__init__(detail)


class UsernameAlreadyExistsError(ConflictError):
    def __init__(self, detail: str = "Username already exists"):
        super().__init__(detail)


class EmailAlreadyExistsError(ConflictError):
    def __init__(self, detail: str = "Email already exists"):
        super().__init__(detail)


class FileTooLargeError(BadRequestError):
    def __init__(self, detail: str = f"File too large, max allowed size is {settings.max_upload_size_bytes // (1024 * 1024)} MB"):
        super().__init__(detail)


class InvalidImageError(BadRequestError):
    def __init__(self, detail: str = "Invalid file, allowed formats: jpg, png, gif, webp"):
        super().__init__(detail)


class NoProfilePictureError(BadRequestError):
    def __init__(self, detail: str = "Profile picture does not exist"):
        super().__init__(detail)