import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import UserModel, UserRole
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import InternalServerError
from ...interfaces.base_component import IBaseComponent
from ...utils.logger import execute_service_method

ICreateUser = IBaseComponent["CreateUser.Request", "CreateUser.Response"]


class CreateUser(ICreateUser):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.USERS)
        self._logger = logger

    class Request(p.BaseModel):
        username: str
        hashed_password: str
        email: str
        role: UserRole

    class Response(p.BaseModel):
        created_user: UserModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        user = UserModel(**request.model_dump(by_alias=True))
        user_data = user.model_dump(by_alias=True)
        inserted_user = self._collection.insert_one(user_data)
        created_user = self._collection.find_one({"_id": inserted_user.inserted_id})
        if not created_user:
            self._logger.error(
                f"Insert user data with id {inserted_user.inserted_id} successfully, but unable to find the created user"
            )
            raise InternalServerError("Insert user data successfully, but unable to find the created user")

        created_user = UserModel(**created_user)
        return self.Response(created_user=created_user)


CreateUserDep = t.Annotated[CreateUser, Depends()]
