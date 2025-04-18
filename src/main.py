import certifi
from bson import CodecOptions, UuidRepresentation
from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient

from src.common.models.house import HouseModel
from src.common.models.yard import YardModel
from src.routers import houses, yards

from .exceptions import AppException, ErrorContent, ErrorJSONResponse, ErrorType
from .middlewares.authenticate_middleware import AuthenticateMiddleware
from .routers import authenticate, organizations, products, tests, users
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


from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi


@app.on_event("startup")
async def init_db():
    client = AsyncIOMotorClient(
        "mongodb+srv://tienliquang:rM5iQV0M6PGeVZ0i@cluster0.v8n2zms.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
        server_api=ServerApi("1"),
        tlsCAFile=certifi.where(),
    )
    db = client["database"]  # your DB name here
    await init_beanie(database=db, document_models=[HouseModel, YardModel])


app.add_middleware(AuthenticateMiddleware)

app.include_router(authenticate.router)

app.include_router(users.router)

app.include_router(organizations.router)

app.include_router(products.router)
app.include_router(houses.router)
app.include_router(yards.router)

# NOTE: for testing purpose only
app.include_router(tests.router)
