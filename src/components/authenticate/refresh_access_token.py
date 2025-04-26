import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.auth import TokenData
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import BadRequestError
from ...interfaces.base_component import IBaseComponent
from ...services.jwt_service import JwtServiceDep
from ...utils.logger import execute_service_method
from .create_refresh_token import CreateRefreshToken, CreateRefreshTokenDep
from .revoke_refresh_token import RevokeRefreshToken, RevokeRefreshTokenDep
from .sign_up import SignUp

IRefreshAccessToken = IBaseComponent["RefreshAccessToken.Request", "RefreshAccessToken.Response"]


class RefreshAccessToken(IRefreshAccessToken):
    def __init__(
        self,
        jwt_service: JwtServiceDep,
        create_refresh_token: CreateRefreshTokenDep,
        revoke_refresh_token: RevokeRefreshTokenDep,
        db: MongoDbDep,
        logger: LoggerDep,
    ) -> None:
        self._jwt_service = jwt_service
        self._create_refresh_token = create_refresh_token
        self._revoke_refresh_token = revoke_refresh_token
        self._db = db
        self._logger = logger
        self._collection = self._db.get_collection(CollectionName.REFRESH_TOKENS)

    class Request(p.BaseModel):
        access_token: str
        refresh_token_id: UUID

    class Response(SignUp.Response):
        pass

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        access_token = request.access_token
        token_data: TokenData | None = None
        try:
            token_data = self._jwt_service.decode_jwt_token(access_token, verify_exp=False)
        except ValueError as e:
            self._logger.error("Failed to decode access token.", exc_info=e)
            raise BadRequestError("Failed to decode access token.")

        if not token_data:
            self._logger.error("Access token is empty.")
            raise BadRequestError("Access token is empty.")

        revoke_refresh_token_response = await self._revoke_refresh_token.aexecute(
            RevokeRefreshToken.Request(access_token=access_token, refresh_token_id=request.refresh_token_id)
        )
        if not revoke_refresh_token_response.success:
            self._logger.error("Failed to revoke refresh token.")
            raise BadRequestError("Failed to revoke refresh token.")

        token_data = self._jwt_service.extend_token_data_expiration(token_data)
        new_access_token = self._jwt_service.encode_jwt_token(token_data)
        create_refresh_token_request = CreateRefreshToken.Request(access_token=new_access_token)
        create_refresh_token_response = await self._create_refresh_token.aexecute(create_refresh_token_request)
        new_refresh_token_id = create_refresh_token_response.refresh_token_id

        return self.Response(
            access_token=new_access_token,
            refresh_token_id=new_refresh_token_id,
        )


RefreshAccessTokenDep = t.Annotated[
    RefreshAccessToken,
    Depends(),
]
