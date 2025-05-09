import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import PyObjectUUID, UserModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method

IGetUserById = IBaseComponent["GetUserById.Request", "GetUserById.Response"]


class GetUserById(IGetUserById):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.USERS)
        self._logger = logger

    class Request(p.BaseModel):
        user_id: PyObjectUUID

    class Response(p.BaseModel):
        user: UserModel | None

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        user_data = self._collection.find_one({"_id": request.user_id})
        if not user_data:
            return self.Response(user=None)

        user = UserModel(**user_data)
        return self.Response(user=user)


GetUserByIdDep = t.Annotated[GetUserById, Depends()]
