import typing as t

import certifi
from beanie import Document, init_beanie
from bson.binary import UuidRepresentation
from bson.codec_options import CodecOptions
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from src.common.models.category import CategoryModel
from src.common.models.organization import OrganizationModel
from src.common.models.product import ProductModel

from ..config import settings
from ..exceptions import InternalServerError
from ..logger import LoggerDep
from .wrapped_db import WrappedDatabase

DATABASE_NAME = "database"


# def create_mongodb_database(logger: LoggerDep) -> Database:
async def create_mongodb_database(logger: LoggerDep) -> WrappedDatabase:
    try:
        codec_options: CodecOptions = CodecOptions(
            uuid_representation=UuidRepresentation.STANDARD,  # use standard UUID representation
            tz_aware=True,  # configure timezone-aware datetime objects
        )
        client: MongoClient = MongoClient(settings.MONGO_URI, server_api=ServerApi("1"), tlsCAFile=certifi.where())
        client.admin.command("ping")
        logger.info("Connected successfully to MongoDB")
        database = client.get_database(DATABASE_NAME, codec_options=codec_options)

        beanie_client: AsyncIOMotorClient = AsyncIOMotorClient(
            settings.MONGO_URI, server_api=ServerApi("1"), tlsCAFile=certifi.where()
        )
        await beanie_client.admin.command("ping")
        logger.info("Beanie Connected successfully to MongoDB")
        # Initialize beanie with the Sample document class and a database
        await init_beanie(
            database=beanie_client.get_database(DATABASE_NAME, codec_options=codec_options),
            document_models=[ProductModel, OrganizationModel],
        )

        # database = beanie_client.get_database(DATABASE_NAME, codec_options=codec_options)

        # return database
        return WrappedDatabase(database)
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True, stack_info=True)
        raise InternalServerError("Failed to connect to MongoDB") from e


MongoDbDep = t.Annotated[WrappedDatabase, Depends(create_mongodb_database)]
# MongoDbDep = t.Annotated[Database, Depends(create_mongodb_database)]
