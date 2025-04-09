from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .exceptions import AppException, ErrorContent, ErrorJSONResponse, ErrorType
from .middlewares.authenticate_middleware import AuthenticateMiddleware
from .routers import authenticate, tests, users
from .services.jwt_service import JwtService

app = FastAPI(dependencies=[Depends(JwtService)])


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    return ErrorJSONResponse(
        error_content=ErrorContent(
            error_type=ErrorType.EXCEPTION,
            error_message=exc.error_message,
        ),
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return ErrorJSONResponse(
        error_content=ErrorContent(
            error_type=ErrorType.REQUEST_VALIDATION,
            error_details=exc.errors(),
        ),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


app.add_middleware(AuthenticateMiddleware)

app.include_router(authenticate.router)

app.include_router(users.router)

# NOTE: for testing purpose only
app.include_router(tests.router)
