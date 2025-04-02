from fastapi import status


class AppException(Exception):
    def __init__(self, status_code: int, error_message: str) -> None:
        self.status_code = status_code
        self.error_message = error_message


class InternalServerError(AppException):
    def __init__(self, error_message: str) -> None:
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=error_message)


class NotFoundError(AppException):
    def __init__(self, error_message: str) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, error_message=error_message)


class BadRequestError(AppException):
    def __init__(self, error_message: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, error_message=error_message)
