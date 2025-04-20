import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.models import UserRole
from ...common.models.user import UserModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import BadRequestError
from ...interfaces.base_component import IBaseComponent
from ...services.jwt_service import JwtServiceDep
from ...utils.logger import execute_service_method
from ..organizations import CreateDefaultOrganization, CreateDefaultOrganizationDep
from ..users import CreateUser, CreateUserDep, GetUserByEmail, GetUserByEmailDep
from .create_refresh_token import CreateRefreshToken, CreateRefreshTokenDep

ISignUp = IBaseComponent["SignUp.Request", "SignUp.Response"]


class SignUp(ISignUp):
    def __init__(
        self,
        create_user: CreateUserDep,
        get_user_by_email: GetUserByEmailDep,
        jwt_service: JwtServiceDep,
        create_refresh_token: CreateRefreshTokenDep,
        db: MongoDbDep,
        logger: LoggerDep,
        create_organization: CreateDefaultOrganizationDep,
    ) -> None:
        self._create_user = create_user
        self._get_user_by_email = get_user_by_email
        self._jwt_service = jwt_service
        self._create_refresh_token = create_refresh_token
        self._collection = db.get_collection(CollectionName.USERS)
        self._logger = logger
        self._create_organization = create_organization

    class Request(p.BaseModel):
        email: p.EmailStr
        password: str = p.Field(min_length=8)
        username: str
        role: UserRole

    class Response(p.BaseModel):
        access_token: str
        refresh_token_id: UUID

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        get_user_by_email_request = GetUserByEmail.Request(email=request.email)
        get_user_by_email_response = await self._get_user_by_email.aexecute(get_user_by_email_request)
        if get_user_by_email_response.user:
            self._logger.error(f"User with email {request.email} already exists.")
            raise BadRequestError(f"User with email {request.email} already exists.")

        self._logger.info(f"User with email {request.email} not found, creating a new user.")
        create_user_request = CreateUser.Request(
            email=request.email,
            hashed_password=self._jwt_service.hash(request.password),
            username=request.username,
            role=request.role,
        )
        create_user_response = await self._create_user.aexecute(create_user_request)

        created_user: UserModel = create_user_response.created_user
        # CreateOrganizationDep handle when create default or non-default organization
        create_default_organization_response = await self._create_organization.aexecute(
            CreateDefaultOrganization.Request(owner_id=created_user.id, owner_name=created_user.username)
        )
        token_data = self._jwt_service.create_user_token_data(
            user=create_user_response.created_user,
            user_role=UserRole.OrganizationAdmin,
            organization_id=create_default_organization_response.created_organization.id,
        )
        access_token = self._jwt_service.encode_jwt_token(token_data)

        create_refresh_token_request = CreateRefreshToken.Request(access_token=access_token)
        create_refresh_token_response = await self._create_refresh_token.aexecute(create_refresh_token_request)
        return self.Response(access_token=access_token, refresh_token_id=create_refresh_token_response.refresh_token_id)


SignUpDep = t.Annotated[SignUp, Depends()]
