import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import InvitationStatus, JoinOrganizationInvitationModel, PyObjectDatetime, PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...interfaces import IBaseComponentWithoutRequest
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method
from ..organizations import GetOrganizationById, GetOrganizationByIdDep
from ..users import GetUserById, GetUserByIdDep

IGetUserInvitations = IBaseComponentWithoutRequest["GetUserInvitations.Response"]

INVITATION_EXPIRATION_DAYS = 3


class GetUserInvitations(IGetUserInvitations):
    def __init__(
        self,
        get_organization_by_id: GetOrganizationByIdDep,
        get_user_by_id: GetUserByIdDep,
        db: MongoDbDep,
        logger: LoggerDep,
        user_context: UserContextDep,
    ) -> None:
        self._get_organization_by_id = get_organization_by_id
        self._get_user_by_id = get_user_by_id
        self._collection = db.get_collection(CollectionName.JOIN_ORGANIZATION_INVITATIONS)
        self._logger = logger
        self._user_context = user_context

    class Sender(p.BaseModel):
        username: str

    class Organization(p.BaseModel):
        name: str

    class UserInvitation(p.BaseModel):
        id: PyObjectUUID = p.Field(alias="id")
        organization: "GetUserInvitations.Organization" = p.Field(alias="organization")
        sender: "GetUserInvitations.Sender" = p.Field(alias="sender")
        status: InvitationStatus = p.Field(alias="status")
        expires_at: PyObjectDatetime = p.Field(alias="expires_at")
        created_at: PyObjectDatetime = p.Field(alias="created_at")
        is_read: bool = p.Field(alias="is_read")

    class Response(p.BaseModel):
        invitations: list["GetUserInvitations.UserInvitation"]

    def _make_query(self, receiver_id: PyObjectUUID) -> dict:
        return {
            "receiver_id": receiver_id,
            "taken_action": None,
            "expires_at": {"$gt": get_utc_now()},
        }

    async def aexecute(self) -> "Response":
        self._logger.info(execute_service_method(self))
        receiver_id = self._user_context.user_id
        query_filter = self._make_query(receiver_id)

        invitations_data = self._collection.find(query_filter)
        invitations = [JoinOrganizationInvitationModel(**invitation_data) for invitation_data in invitations_data]

        user_invitations = []
        for invitation in invitations:
            organization_id = invitation.organization_id
            get_organization_by_id_response = await self._get_organization_by_id.aexecute(
                GetOrganizationById.Request(id=organization_id)
            )
            if not get_organization_by_id_response.organization:
                self._logger.error(f"Organization with id {organization_id} not found.")
                continue

            sender_id = invitation.sender_id
            get_user_by_id_response = await self._get_user_by_id.aexecute(GetUserById.Request(user_id=sender_id))
            if not get_user_by_id_response.user:
                self._logger.error(f"User with id {sender_id} not found.")
                continue

            user_invitation = self.UserInvitation(
                id=invitation.id,
                organization=self.Organization(name=get_organization_by_id_response.organization.name),
                sender=self.Sender(username=get_user_by_id_response.user.username),
                status=invitation.status,
                expires_at=invitation.expires_at,
                created_at=invitation.created_at,
                is_read=invitation.is_read,
            )
            user_invitations.append(user_invitation)

        return self.Response(invitations=user_invitations)


GetUserInvitationsDep = t.Annotated[GetUserInvitations, Depends()]
