import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.auth import TokenData, UserContextDep
from ...common.models import OrganizationModel, UserRole
from ...dependencies import LoggerDep
from ...exceptions import BadRequestError
from ...interfaces.base_component import IBaseComponent
from ...services.jwt_service import JwtServiceDep
from ...utils.logger import execute_service_method
from ..authenticate import CreateRefreshToken, CreateRefreshTokenDep, RevokeRefreshToken, RevokeRefreshTokenDep, SignUp
from ..organizations.get_organization_by_id import GetOrganizationByIdDep

ISwitchOrganization = IBaseComponent["SwitchOrganization.Request", "SwitchOrganization.Response"]


class SwitchOrganization(ISwitchOrganization):
    def __init__(
        self,
        jwt_service: JwtServiceDep,
        create_refresh_token: CreateRefreshTokenDep,
        revoke_refresh_token: RevokeRefreshTokenDep,
        logger: LoggerDep,
        get_organization: GetOrganizationByIdDep,
        user_context: UserContextDep,
    ) -> None:
        self._jwt_service = jwt_service
        self._create_refresh_token = create_refresh_token
        self._revoke_refresh_token = revoke_refresh_token
        self._logger = logger
        self._get_organization = get_organization
        self._user_context = user_context

    class Request(p.BaseModel):
        access_token: str
        refresh_token_id: UUID
        organization_id: UUID

    class Response(SignUp.Response):
        pass

    def _update_token_data(self, token_data: TokenData, organization: OrganizationModel) -> TokenData:
        token_data.organization_id = organization.id
        token_data.role = (
            UserRole.OrganizationAdmin if token_data.user_id == organization.owner_id else UserRole.OrganizationMember
        )
        return token_data

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        token_data = TokenData(**self._user_context.model_dump())
        requested_organization_id = request.organization_id
        if token_data.organization_id == requested_organization_id:
            self._logger.info(f"Requested organization id {requested_organization_id} is the same as the current one.")
            raise BadRequestError("Requested organization is the same as the current one.")

        revoke_refresh_token_response = await self._revoke_refresh_token.aexecute(
            RevokeRefreshToken.Request(access_token=request.access_token, refresh_token_id=request.refresh_token_id)
        )
        if not revoke_refresh_token_response.success:
            self._logger.error("Failed to revoke refresh token.")
            raise BadRequestError("Failed to revoke refresh token.")

        get_organization_by_id_response = await self._get_organization.aexecute(
            GetOrganizationByIdDep.Request(id=requested_organization_id)
        )
        token_data = self._update_token_data(token_data, get_organization_by_id_response.organization)
        new_access_token = self._jwt_service.encode_jwt_token(token_data)
        create_refresh_token_request = CreateRefreshToken.Request(access_token=new_access_token)
        create_refresh_token_response = await self._create_refresh_token.aexecute(create_refresh_token_request)
        new_refresh_token_id = create_refresh_token_response.refresh_token_id

        return self.Response(
            access_token=new_access_token,
            refresh_token_id=new_refresh_token_id,
        )


SwitchOrganizationDep = t.Annotated[
    SwitchOrganization,
    Depends(),
]
