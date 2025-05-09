import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import BadRequestError
from ...interfaces import IBaseComponent
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method
from .get_me import GetMe
from .get_user_by_id import GetUserByIdDep

IUpdateUser = IBaseComponent["UpdateUser.Request", "UpdateUser.Response"]


class UpdateUser(IUpdateUser):
    def __init__(self, get_user_by_id: GetUserByIdDep, db: MongoDbDep, logger: LoggerDep) -> None:
        self._get_user_by_id = get_user_by_id
        self._collection = db.get_collection(CollectionName.USERS)
        self._logger = logger

    class HttpRequest(p.BaseModel):
        username: str | None = p.Field(default=None)

    class Request(HttpRequest, p.BaseModel):
        user_id: PyObjectUUID

    class Response(p.BaseModel):
        updated_user: GetMe.User

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        update_data = request.model_dump(exclude={"user_id"}, exclude_none=True)

        if not update_data:
            self._logger.info(f"No fields to update for user id {request.user_id}")
            raise BadRequestError("No fields to update")

        get_user_by_id_response = await self._get_user_by_id.aexecute(GetUserByIdDep.Request(user_id=request.user_id))
        user = get_user_by_id_response.user
        if not user:
            self._logger.error(f"User with id {request.user_id} not found")
            raise BadRequestError(f"User with id {request.user_id} not found")

        updated_user = user.model_copy(update=update_data)
        updated_user.updated_at = get_utc_now()
        self._collection.update_one({"_id": updated_user.id}, {"$set": updated_user.model_dump(exclude={"id"})})
        return self.Response(updated_user=GetMe.User(**updated_user.model_dump()))


UpdateUserDep = t.Annotated[UpdateUser, Depends()]
