from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .exceptions import AppException, ErrorContent, ErrorJSONResponse, ErrorType
from .middlewares.authenticate_middleware import AuthenticateMiddleware
from .routers import authenticate, design_projects, join_organization_invitations, organizations, users, websocket
from .services.jwt_service import JwtService

app = FastAPI(dependencies=[Depends(JwtService)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

app.include_router(organizations.router)

app.include_router(join_organization_invitations.router)

app.include_router(design_projects.router)

app.include_router(websocket.router)
