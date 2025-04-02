from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .exceptions import AppException
from .routers import tests, users

app = FastAPI()


@app.exception_handler(AppException)
def custom_exception_handler(request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_message": exc.error_message},
    )


app.include_router(users.router)

# NOTE: for testing purpose only
app.include_router(tests.router)
