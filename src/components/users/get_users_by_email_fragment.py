import typing as t

import pydantic as p
from fastapi import Depends
from pymongo.cursor import Cursor

from ...common.models import UserModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method

IGetUserByEmailFragment = IBaseComponent["GetUserByEmailFragment.Request", "GetUserByEmailFragment.Response"]


class GetUserByEmailFragment(IGetUserByEmailFragment):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._db = db
        self._logger = logger
        self._collection = self._db.get_collection(CollectionName.USERS)

    class Request(p.BaseModel):
        email_fragment: str

    class Response(p.BaseModel):
        users: t.List["UserModel"] | None

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        email_fragment = request.email_fragment
        regex_pattern = f".*{email_fragment}.*"
        users_data: Cursor = self._collection.find(
            {"email": {"$regex": regex_pattern, "$options": "i"}}
        )  # "$options": "i" ~ case ignore
        if not users_data:
            return self.Response(users=[])

        users = [UserModel(**user_data) for user_data in users_data]
        return self.Response(users=users)


GetUserByEmailFragmentDep = t.Annotated[GetUserByEmailFragment, Depends()]
