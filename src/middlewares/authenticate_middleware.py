import typing as t

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from ..common.auth import TokenData
from ..config import create_settings
from ..constants.request import HeaderKey, RequestMethod
from ..constants.router import ApiPath
from ..exceptions import ErrorContent, ErrorJSONResponse, ErrorType
from ..logger import create_logger
from ..services.jwt_service import JwtService


class AuthenticateMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._jwt_service = self._create_jwt_service()

    # TODO: find a way to access global dependencies if possible
    def _create_jwt_service(self) -> JwtService:
        return JwtService(
            settings=create_settings(),
            logger=create_logger(),
        )

    def _is_swagger_url_paths(self, url_path: str) -> bool:
        return url_path.startswith(("/docs", "/redoc", "/openapi.json"))

    def _is_authentication_url_path(self, url_path: str) -> bool:
        return url_path.startswith(ApiPath.AUTHENTICATE)

    def _is_test_url_path(self, url_path: str) -> bool:
        return url_path.startswith(ApiPath.TESTS)

    async def dispatch(self, request: Request, call_next: t.Callable) -> JSONResponse:
        url_path = request.url.path

        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == RequestMethod.OPTIONS:
            return await call_next(request)

        if self._is_swagger_url_paths(url_path):
            return await call_next(request)

        if self._is_authentication_url_path(url_path):
            return await call_next(request)

        # NOTE: skip authentication for the tests endpoint
        # This is for testing purpose only
        if self._is_test_url_path(url_path):
            return await call_next(request)

        auth_header = request.headers.get(HeaderKey.AUTHORIZATION)
        if not auth_header or not auth_header.startswith("Bearer "):
            return ErrorJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_content=ErrorContent(
                    error_type=ErrorType.AUTHENTICATION,
                    error_message="Missing or invalid Authorization header.",
                ),
            )

        auth_splits = auth_header.split(" ")
        if len(auth_splits) != 2:
            return ErrorJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_content=ErrorContent(
                    error_type=ErrorType.AUTHENTICATION,
                    error_message="Invalid Authorization header format.",
                ),
            )

        bearer_token = auth_splits[1].strip()
        if not bearer_token:
            return ErrorJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_content=ErrorContent(
                    error_type=ErrorType.AUTHENTICATION,
                    error_message="Missing token in Authorization header.",
                ),
            )

        try:
            token_data = self._jwt_service.decode_jwt_token(bearer_token)
            self._add_token_data_to_request_context(request, token_data)
        except ValueError as e:
            return ErrorJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_content=ErrorContent(
                    error_type=ErrorType.AUTHENTICATION,
                    error_message=str(e),
                ),
            )

        return await call_next(request)

    def _add_token_data_to_request_context(self, request: Request, token_data: TokenData) -> None:
        if not hasattr(request.state, "token_data"):
            request.state.token_data = token_data
