from core.exceptions import UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    def __init__(self, detail: str = "Incorrect credentials"):
        super().__init__(detail=detail)


class InvalidTokenError(UnauthorizedError):
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(detail=detail)
