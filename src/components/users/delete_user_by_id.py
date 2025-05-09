import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import InternalServerError, NotFoundError
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method

IDeleteUserById = IBaseComponent["DeleteUserById.Request", "DeleteUserById.Response"]


# TODO: handle delete user
class DeleteUserById(IDeleteUserById):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.USERS)
        self._logger = logger

    class Request(p.BaseModel):
        user_id: PyObjectUUID

    class Response(p.BaseModel):
        success: bool

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        result = self._collection.delete_one({"_id": request.user_id})
        if result.deleted_count == 0:
            self._logger.info(f"User with id {request.user_id} not found")
            raise NotFoundError(f"User with id {request.user_id} not found")

        if result.deleted_count != 1:
            self._logger.error(f"Unexpected deletion count for user id {request.user_id}")
            raise InternalServerError("Unexpected error occurred during user deletion")

        return self.Response(success=True)


DeleteUserByIdDep = t.Annotated[DeleteUserById, Depends()]
