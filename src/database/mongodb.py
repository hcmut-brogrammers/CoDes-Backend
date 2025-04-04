import typing as t

from bson.binary import UuidRepresentation
from bson.codec_options import CodecOptions
from fastapi import Depends
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from ..config import settings
from ..exceptions import InternalServerError
from ..logger import LoggerDep

DATABASE_NAME = "database"


def create_mongodb_database(logger: LoggerDep) -> Database:
    try:
        codec_options: CodecOptions = CodecOptions(
            uuid_representation=UuidRepresentation.STANDARD,  # use standard UUID representation
            tz_aware=True,  # configure timezone-aware datetime objects
        )
        client: MongoClient = MongoClient(settings.MONGO_URI, server_api=ServerApi("1"))
        client.admin.command("ping")
        logger.info("Connected successfully to MongoDB")
        database = client.get_database(DATABASE_NAME, codec_options=codec_options)
        return database
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True, stack_info=True)
        raise InternalServerError("Failed to connect to MongoDB") from e


MongoDbDep = t.Annotated[Database, Depends(create_mongodb_database)]
