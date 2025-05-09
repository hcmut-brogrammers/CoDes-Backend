import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import PyObjectUUID, RefreshTokenModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...interfaces import IBaseComponent
from ...services.jwt_service import JwtServiceDep
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method

IRevokeRefreshToken = IBaseComponent["RevokeRefreshToken.Request", "RevokeRefreshToken.Response"]


class RevokeRefreshToken(IRevokeRefreshToken):
    def __init__(self, db: MongoDbDep, jwt_service: JwtServiceDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.REFRESH_TOKENS)
        self._jwt_service = jwt_service
        self._logger = logger

    class Request(p.BaseModel):
        access_token: str
        refresh_token_id: PyObjectUUID

    class Response(p.BaseModel):
        success: bool

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        find_one_result = self._collection.find_one({"_id": request.refresh_token_id})
        if not find_one_result:
            self._logger.error("Invalid refresh token id.")
            return self.Response(success=False)

        refresh_token = RefreshTokenModel(**find_one_result)
        is_hashed_access_token_valid = self._jwt_service.verify_password(
            request.access_token,
            refresh_token.hashed_access_token,
        )
        if not is_hashed_access_token_valid:
            self._logger.error("Hashed access token is invalid.")
            return self.Response(success=False)

        if refresh_token.revoked_at:
            self._logger.error("Refresh token is already revoked.")
            return self.Response(success=False)

        utc_now = get_utc_now()
        if refresh_token.expired_at < utc_now:
            self._logger.error("Refresh token is expired.")
            return self.Response(success=False)

        refresh_token.revoked_at = utc_now
        self._collection.update_one(
            {"_id": request.refresh_token_id},
            {"$set": {"revoked_at": refresh_token.revoked_at}},
        )

        return self.Response(success=True)


RevokeRefreshTokenDep = t.Annotated[RevokeRefreshToken, Depends()]
