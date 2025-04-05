import typing as t

from fastapi import Depends, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from ..common.auth import TokenData
from ..config import create_settings
from ..constants.router import ApiPath
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

    async def dispatch(self, request: Request, call_next: t.Callable) -> JSONResponse:
        # Skip authentication for the authentication endpoint
        if request.url.path.startswith(ApiPath.AUTHENTICATE):
            return await call_next(request)

        # NOTE: skip authentication for the tests endpoint
        # This is for testing purpose only
        if request.url.path.startswith(ApiPath.TESTS):
            return await call_next(request)

        # TODO: refactor JSONResponse with exception if possible
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"error_message": "Missing or invalid Authorization header"})

        auth_splits = auth_header.split(" ")
        if len(auth_splits) != 2:
            return JSONResponse(status_code=401, content={"error_message": "Invalid Authorization header format"})

        bearer_token = auth_splits[1].strip()
        if not bearer_token:
            return JSONResponse(status_code=401, content={"error_message": "Missing token in Authorization header"})

        try:
            token_data = self._jwt_service.decode_jwt_token(bearer_token)
            self._add_token_data_to_request_context(request, token_data)
        except ValueError as e:
            return JSONResponse(status_code=401, content={"error_message": str(e)})

        return await call_next(request)

    def _add_token_data_to_request_context(self, request: Request, token_data: TokenData) -> None:
        if not hasattr(request.state, "token_data"):
            request.state.token_data = token_data
