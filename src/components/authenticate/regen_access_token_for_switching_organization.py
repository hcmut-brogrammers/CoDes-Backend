import typing as t
from datetime import timedelta
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.auth import TokenData
from ...common.models import RefreshTokenModel, UserRole
from ...components.organizations.get_organization_by_id import GetOrganizationByIdDep
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import BadRequestError
from ...interfaces.base_component import IBaseComponent
from ...services.jwt_service import JwtServiceDep
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method
from .create_refresh_token import REFRESH_TOKEN_EXPIRES_DAYS, CreateRefreshToken, CreateRefreshTokenDep
from .sign_up import SignUp

IRegen_access_token_for_switching_organization = IBaseComponent[
    "Regen_access_token_for_switching_organization.Request", "Regen_access_token_for_switching_organization.Response"
]


class Regen_access_token_for_switching_organization(IRegen_access_token_for_switching_organization):
    def __init__(
        self,
        jwt_service: JwtServiceDep,
        create_refresh_token: CreateRefreshTokenDep,
        db: MongoDbDep,
        logger: LoggerDep,
        get_organization: GetOrganizationByIdDep,
    ) -> None:
        self._jwt_service = jwt_service
        self._create_refresh_token = create_refresh_token
        self._db = db
        self._logger = logger
        self._refresh_token_collection = self._db.get_collection(CollectionName.REFRESH_TOKENS)
        self._get_organization = get_organization

    class Request(p.BaseModel):
        organization_id: UUID
        access_token: str
        refresh_token_id: UUID

    class Response(SignUp.Response):
        pass

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        token_data: TokenData | None = None
        try:
            token_data = self._jwt_service.decode_jwt_token(request.access_token, verify_exp=False)
        except ValueError as e:
            self._logger.error("Failed to decode access token.", exc_info=e)
            raise BadRequestError("Failed to decode access token.")

        if not token_data:
            self._logger.error("Access token is empty.")
            raise BadRequestError("Access token is empty.")

        find_one_result = self._refresh_token_collection.find_one({"_id": request.refresh_token_id})
        if not find_one_result:
            self._logger.error("Invalid refresh token id.")
            raise BadRequestError("Invalid refresh token id.")

        # is_hashed_access_token_valid = self._jwt_service.verify_password(
        #     request.access_token,
        #     find_one_result["hashed_access_token"],
        # )
        # if not is_hashed_access_token_valid:
        #     self._logger.error("Hashed access token is invalid.")
        #     raise BadRequestError("Hashed access token is invalid.")

        # refresh_token = RefreshTokenModel(**find_one_result)
        # if refresh_token.revoked_at:
        #     self._logger.error("Refresh token is already revoked.")
        #     raise BadRequestError("Refresh token is already revoked.")

        # if refresh_token.expired_at < get_utc_now():
        #     self._logger.error("Refresh token is expired.")
        #     raise BadRequestError("Refresh token is expired.")

        # refresh_token.revoked_at = get_utc_now()
        # self._refresh_token_collection.update_one(
        #     {"_id": request.refresh_token_id},
        #     {"$set": {"revoked_at": refresh_token.revoked_at}},
        # )

        request_organization_id = request.organization_id
        get_organization = await self._get_organization.aexecute(
            GetOrganizationByIdDep.Request(_id=request_organization_id)
        )

        # update token data
        token_data.organization_id = request_organization_id
        if token_data.user_id is get_organization.organization.owner_id:
            token_data.role = UserRole.OrganizationAdmin
        else:
            token_data.role = UserRole.OrganizationMember
        ## [?] update expired time for re-gen access token
        # token_data.exp = int(self._jwt_service._get_access_token_expires().timestamp())

        new_access_token = self._jwt_service.encode_jwt_token(token_data)
        # create_refresh_token_request = CreateRefreshToken.Request(access_token=new_access_token)
        # create_refresh_token_response = await self._create_refresh_token.aexecute(create_refresh_token_request)
        # new_refresh_token_id = create_refresh_token_response.refresh_token_id

        update_data = {"hashed_access_token": self._jwt_service.hash(new_access_token)}  # kiếm thêm password của user?
        updated_refresh_token = RefreshTokenModel(**find_one_result).model_copy(update=update_data)

        self._refresh_token_collection.update_one(
            {"_id": updated_refresh_token.id}, {"$set": updated_refresh_token.model_dump(exclude={"id"})}
        )

        return self.Response(
            access_token=new_access_token,
            refresh_token_id=request.refresh_token_id,
        )


Regen_access_token_for_switching_organizationDep = t.Annotated[
    Regen_access_token_for_switching_organization,
    Depends(),
]
