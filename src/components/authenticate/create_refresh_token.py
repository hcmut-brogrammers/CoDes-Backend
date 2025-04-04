import typing as t
from datetime import timedelta
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.models import RefreshTokenModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import InternalServerError
from ...interfaces.base_component import IBaseComponent
from ...services.jwt_service import JwtServiceDep
from ...utils.common import get_utc_now

ICreateRefreshToken = IBaseComponent["CreateRefreshToken.Request", "CreateRefreshToken.Response"]

REFRESH_TOKEN_EXPIRES_DAYS = 2


class CreateRefreshToken(ICreateRefreshToken):
    def __init__(self, jwt_service: JwtServiceDep, db: MongoDbDep, logger: LoggerDep) -> None:
        self._jwt_service = jwt_service
        self._db = db
        self._logger = logger
        self._collection = self._db.get_collection(CollectionName.REFRESH_TOKENS)

    class Request(p.BaseModel):
        access_token: str

    class Response(p.BaseModel):
        refresh_token_id: UUID

    async def aexecute(self, request: "Request") -> "Response":
        hashed_access_token = self._jwt_service.hash(request.access_token)
        expired_at = get_utc_now() + timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS)
        refresh_token = RefreshTokenModel(
            hashed_access_token=hashed_access_token, expired_at=expired_at, revoked_at=None
        )
        insert_one_result = self._collection.insert_one(refresh_token.model_dump(by_alias=True))
        find_one_result = self._collection.find_one({"_id": insert_one_result.inserted_id})
        if not find_one_result:
            self._logger.error("Insert refresh token but failed to retrieve it.")
            raise InternalServerError("Failed to create refresh token.")

        created_refresh_token = RefreshTokenModel(**find_one_result)
        return self.Response(refresh_token_id=created_refresh_token.id)


CreateRefreshTokenDep = t.Annotated[CreateRefreshToken, Depends()]
