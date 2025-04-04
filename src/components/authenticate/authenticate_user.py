import typing as t

import pydantic as p
from fastapi import Depends

from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import BadRequestError
from ...interfaces import IBaseComponent
from ...services.jwt_service import JwtServiceDep
from ...utils.logger import execute_service_method
from ..users import GetUserByEmail, GetUserByEmailDep
from .create_refresh_token import CreateRefreshToken, CreateRefreshTokenDep
from .sign_up import SignUp

IAuthenticateUser = IBaseComponent["AuthenticateUser.Request", "AuthenticateUser.Response"]


class AuthenticateUser(IAuthenticateUser):
    def __init__(
        self,
        get_user_by_email: GetUserByEmailDep,
        jwt_service: JwtServiceDep,
        create_refresh_token: CreateRefreshTokenDep,
        db: MongoDbDep,
        logger: LoggerDep,
    ) -> None:
        self._get_user_by_email = get_user_by_email
        self._jwt_service = jwt_service
        self._create_refresh_token = create_refresh_token
        self._db = db
        self._logger = logger

    class Request(p.BaseModel):
        email: str
        password: str

    class Response(SignUp.Response):
        pass

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        get_user_by_email_request = GetUserByEmail.Request(email=request.email)
        get_user_by_email_response = await self._get_user_by_email.aexecute(get_user_by_email_request)
        current_user = get_user_by_email_response.user
        if not current_user:
            self._logger.info(f"User with email {request.email} not found.")
            raise BadRequestError(f"User with email {request.email} not found.")

        is_password_matched = self._jwt_service.verify_password(request.password, current_user.hashed_password)
        if not is_password_matched:
            self._logger.error(f"Password for user {request.email} is incorrect.")
            raise BadRequestError(f"Password for user {request.email} is incorrect.")

        token_data = self._jwt_service.create_user_token_data(current_user)
        access_token = self._jwt_service.encode_jwt_token(token_data)

        create_refresh_token_request = CreateRefreshToken.Request(access_token=access_token)
        create_refresh_token_response = await self._create_refresh_token.aexecute(create_refresh_token_request)
        return self.Response(access_token=access_token, refresh_token_id=create_refresh_token_response.refresh_token_id)


AuthenticateUserDep = t.Annotated[AuthenticateUser, Depends()]
