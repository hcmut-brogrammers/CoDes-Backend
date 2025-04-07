from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from .exceptions import AppException
from .middlewares.authenticate_middleware import AuthenticateMiddleware
from .routers import authenticate, organizations, tests, users
from .services.jwt_service import JwtService

app = FastAPI(dependencies=[Depends(JwtService)])


@app.exception_handler(AppException)
def custom_exception_handler(request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_message": exc.error_message},
    )


app.add_middleware(AuthenticateMiddleware)

app.include_router(authenticate.router)

app.include_router(users.router)

app.include_router(organizations.router)

# NOTE: for testing purpose only
app.include_router(tests.router)
