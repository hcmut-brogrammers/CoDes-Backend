import typing as t
from enum import Enum

import pydantic as p
from fastapi import status
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask


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


class ForbiddenError(AppException):
    def __init__(self, error_message: str) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, error_message=error_message)


class BadRequestError(AppException):
    def __init__(self, error_message: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, error_message=error_message)


class UnauthorizedError(AppException):
    def __init__(self, error_message: str) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, error_message=error_message)


class ErrorType(str, Enum):
    EXCEPTION = "exception_error"
    AUTHENTICATION = "authentication_error"
    REQUEST_VALIDATION = "request_validation_error"


class ErrorContent(p.BaseModel):
    error_type: ErrorType = p.Field(alias="error_type")
    error_message: str | None = p.Field(alias="error_message", default=None)
    error_details: t.Any | None = p.Field(alias="error_details", default=None)

    model_config = p.ConfigDict(use_enum_values=True)


class ErrorContentWithStatusCode(ErrorContent):
    status_code: int = p.Field(alias="status_code")


class ErrorJSONResponse(JSONResponse):
    def __init__(
        self,
        error_content: ErrorContent,
        status_code: int,
        headers: t.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        error_content_with_status_code = ErrorContentWithStatusCode(
            **error_content.model_dump(),
            status_code=status_code,
        )
        super().__init__(error_content_with_status_code.model_dump(), status_code, headers, media_type, background)
