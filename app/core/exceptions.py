from fastapi import HTTPException, status

class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictError(HTTPException):
    def __init__(self, detail: str = "Conflict occurred"):
        self.detail = detail
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
