from core.exceptions import ConflictError, NotFoundError


class UserNotFoundError(NotFoundError):
    def __init__(self, detail: str = "User not found"):
        super().__init__(detail)


class UsernameAlreadyExistsError(ConflictError):
    def __init__(self, detail: str = "Username already exists"):
        super().__init__(detail)


class EmailAlreadyExistsError(ConflictError):
    def __init__(self, detail: str = "Email already exists"):
        super().__init__(detail)
