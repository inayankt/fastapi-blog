from core.exceptions import BadRequestError, ForbiddenError, UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    def __init__(self, detail: str = "Incorrect credentials"):
        super().__init__(detail)


class InvalidTokenError(UnauthorizedError):
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(detail)


class NotPostOwnerError(ForbiddenError):
    def __init__(self, detail: str = "Not authorized to alter this post"):
        super().__init__(detail)


class NotCurrentUserError(ForbiddenError):
    def __init__(self, detail: str = "Not authorized to alter this user"):
        super().__init__(detail)


class InvalidResetTokenError(BadRequestError):
    def __init__(self, detail: str = "Invalid or expired reset token"):
        super().__init__(detail)


class IncorrectCurrentPasswordError(BadRequestError):
    def __init__(self, detail: str = "Current password is incorrect"):
        super().__init__(detail)
