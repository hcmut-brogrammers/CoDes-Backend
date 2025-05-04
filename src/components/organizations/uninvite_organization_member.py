import typing as t

import pydantic as p
from fastapi import Depends

from ...common.auth import UserContextDep
from ...common.models import PyObjectUUID, UserRole
from ...dependencies import LoggerDep
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method
from ..organizations import GetOrganizationById, GetOrganizationByIdDep
from ..users import RemoveUserFromOrganization, RemoveUserFromOrganizationDep

IUninviteOrganzationMember = IBaseComponent["UninviteOrganzationMember.Request", "UninviteOrganzationMember.Response"]


class UninviteOrganzationMember(IUninviteOrganzationMember):
    def __init__(
        self,
        get_organization_by_id: GetOrganizationByIdDep,
        user_context: UserContextDep,
        logger: LoggerDep,
        remove_user_from_organization: RemoveUserFromOrganizationDep,
    ) -> None:
        self._get_organization_by_id = get_organization_by_id
        self._user_context = user_context
        self._logger = logger
        self._remove_user_from_organization = remove_user_from_organization

    class Request(p.BaseModel):
        member_id: PyObjectUUID

    class Response(p.BaseModel):
        success: bool

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        if self._user_context.role != UserRole.OrganizationAdmin:
            self._logger.error("User is not an organization admin.")
            return self.Response(success=False)

        # Check if the user is a member of the organization
        organization_id = self._user_context.organization_id
        get_organization_by_id_response = await self._get_organization_by_id.aexecute(
            GetOrganizationById.Request(id=organization_id)
        )
        organization = get_organization_by_id_response.organization
        if not organization:
            self._logger.error(f"Organization {organization_id} not found.")
            return self.Response(success=False)

        member_id = request.member_id
        member_ids = [member.member_id for member in organization.members]
        if member_id not in member_ids:
            self._logger.error(f"User {member_id} is not a member of the organization.")
            return self.Response(success=False)

        remove_user_from_organization_request = RemoveUserFromOrganization.Request(
            organization_id=organization_id,
            user_id=member_id,
        )
        remove_user_from_organization_response = await self._remove_user_from_organization.aexecute(
            remove_user_from_organization_request
        )
        if not remove_user_from_organization_response:
            self._logger.error(f"Failed to remove user {member_id} from organization {organization_id}.")
            return self.Response(success=False)

        return self.Response(success=True)


UninviteOrganzationMemberDep = t.Annotated[UninviteOrganzationMember, Depends()]
