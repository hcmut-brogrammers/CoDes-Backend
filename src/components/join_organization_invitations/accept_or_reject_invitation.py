import typing as t

import pydantic as p
from fastapi import Depends

from ...common.auth import UserContextDep
from ...common.models import (
    InvitationStatus,
    InviteeAction,
    JoinOrganizationInvitationModel,
    PyObjectUUID,
    TakenAction,
    UserRole,
)
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...interfaces import IBaseComponent
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method
from ..organizations import GetOrganizationById, GetOrganizationByIdDep
from ..users import AddUserToOrganization, AddUserToOrganizationDep, GetUserById, GetUserByIdDep

IAcceptOrRejectInvitation = IBaseComponent["AcceptOrRejectInvitation.Request", "AcceptOrRejectInvitation.Response"]


class AcceptOrRejectInvitation(IAcceptOrRejectInvitation):
    def __init__(
        self,
        get_user_by_id: GetUserByIdDep,
        get_organization_by_id: GetOrganizationByIdDep,
        user_context: UserContextDep,
        db: MongoDbDep,
        logger: LoggerDep,
        add_user_to_organization: AddUserToOrganizationDep,
    ) -> None:
        self._get_user_by_id = get_user_by_id
        self._get_organization_by_id = get_organization_by_id
        self._user_context = user_context
        self._invitation_collection = db.get_collection(CollectionName.JOIN_ORGANIZATION_INVITATIONS)
        self._logger = logger
        self._add_user_to_organization = add_user_to_organization

    class Request(p.BaseModel):
        invitation_id: PyObjectUUID
        action: InviteeAction

    class Response(p.BaseModel):
        success: bool

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        invitation_data = self._invitation_collection.find_one({"_id": request.invitation_id})
        if not invitation_data:
            self._logger.error(f"Invitation with ID {request.invitation_id} not found.")
            return self.Response(success=False)

        invitation = JoinOrganizationInvitationModel(**invitation_data)
        if invitation.status != InvitationStatus.Pending:
            self._logger.error("Invitation is not in a pending state.")
            return self.Response(success=False)

        if invitation.taken_action:
            self._logger.error("Invitation has already been taken action on.")
            return self.Response(success=False)

        now = get_utc_now()
        if invitation.expires_at < now:
            self._logger.error("Invitation has expired.")
            return self.Response(success=False)

        if self._user_context.user_id != invitation.receiver_id:
            self._logger.error("User is not authorized to accept or reject this invitation.")
            return self.Response(success=False)

        get_organization_by_id_response = await self._get_organization_by_id.aexecute(
            GetOrganizationById.Request(id=invitation.organization_id)
        )
        organization = get_organization_by_id_response.organization
        if not organization:
            self._logger.error(f"Organization with ID {invitation.organization_id} not found.")
            return self.Response(success=False)

        get_user_by_id_response = await self._get_user_by_id.aexecute(
            GetUserById.Request(user_id=invitation.receiver_id)
        )
        receiver = get_user_by_id_response.user
        if not receiver:
            self._logger.error(f"User with ID {invitation.receiver_id} not found.")
            return self.Response(success=False)

        invitee_action = request.action
        if invitee_action == InviteeAction.Accept:
            member_ids = [member.member_id for member in organization.members]
            if receiver.id in member_ids:
                self._logger.error(f"User {receiver.id} is already a member of organization {organization.id}.")
                return self.Response(success=False)

            add_user_to_organization_request = AddUserToOrganization.Request(
                organization_id=organization.id,
                user_id=receiver.id,
                role=UserRole.OrganizationMember,
            )
            add_user_to_organization_response = await self._add_user_to_organization.aexecute(
                add_user_to_organization_request
            )
            if not add_user_to_organization_response:
                self._logger.error(f"Failed to add user {receiver.id} to organization {organization.id}")
                return self.Response(success=False)

        invitation.taken_action = TakenAction(action=invitee_action, taken_at=now)
        invitation.status = InvitationStatus.Completed
        invitation.updated_at = now
        self._invitation_collection.update_one({"_id": invitation.id}, {"$set": invitation.model_dump(exclude={"id"})})
        return self.Response(success=True)


AcceptOrRejectInvitationDep = t.Annotated[AcceptOrRejectInvitation, Depends()]
