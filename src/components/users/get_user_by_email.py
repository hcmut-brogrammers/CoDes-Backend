import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import UserModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method

IGetUserByEmail = IBaseComponent["GetUserByEmail.Request", "GetUserByEmail.Response"]


class GetUserByEmail(IGetUserByEmail):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._db = db
        self._logger = logger
        self._collection = self._db.get_collection(CollectionName.USERS)

    class Request(p.BaseModel):
        email: str

    class Response(p.BaseModel):
        user: UserModel | None

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        result = self._collection.find_one({"email": request.email})
        if not result:
            return self.Response(user=None)

        user = UserModel(**result)
        return self.Response(user=user)


GetUserByEmailDep = t.Annotated[GetUserByEmail, Depends()]
