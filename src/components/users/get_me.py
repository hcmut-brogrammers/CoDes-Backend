import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import PyObjectDatetime, PyObjectUUID, UserRole
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import NotFoundError
from ...interfaces.base_component import IBaseComponentWithoutRequest
from ...utils.logger import execute_service_method
from .get_user_by_id import GetUserById, GetUserByIdDep

IGetMe = IBaseComponentWithoutRequest["GetMe.Response"]


class GetMe(IGetMe):
    def __init__(
        self, get_user_by_id: GetUserByIdDep, user_context: UserContextDep, db: MongoDbDep, logger: LoggerDep
    ) -> None:
        self._get_user_by_id = get_user_by_id
        self._user_context = user_context
        self._collection = db.get_collection(CollectionName.USERS)
        self._logger = logger

    class User(p.BaseModel):
        id: PyObjectUUID
        username: str
        email: str
        role: UserRole
        created_at: PyObjectDatetime
        updated_at: PyObjectDatetime

    class Response(p.BaseModel):
        user: "GetMe.User"

    async def aexecute(self) -> "Response":
        self._logger.info(execute_service_method(self))
        user_id = self._user_context.user_id
        get_user_by_id_response = await self._get_user_by_id.aexecute(GetUserById.Request(user_id=user_id))
        if not get_user_by_id_response.user:
            self._logger.error(f"User with id {user_id} not found.")
            raise NotFoundError(f"User with id {user_id} not found.")

        user = get_user_by_id_response.user
        return self.Response(
            user=self.User(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        )


GetMeDep = t.Annotated[GetMe, Depends()]
