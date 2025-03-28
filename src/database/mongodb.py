import fastapi as p
import typing as t
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from ..config import settings

TEST_DATABASE_NAME = "students"


def create_mongodb_database() -> Database:
    try:
        client: MongoClient = MongoClient(settings.MONGO_URI, server_api=ServerApi("1"))
        client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")

        database = client.get_database(TEST_DATABASE_NAME)
        return database
    except Exception as e:
        raise e


MongoDbDep = t.Annotated[Database, p.Depends(create_mongodb_database)]
