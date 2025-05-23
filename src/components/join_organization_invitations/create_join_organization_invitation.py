import typing as t
from datetime import timedelta

import pydantic as p
from fastapi import Depends

from ...common.models import JoinOrganizationInvitationModel, PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import BadRequestError, InternalServerError
from ...interfaces import IBaseComponent
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method

ICreateJoinOrganizationInvitation = IBaseComponent[
    "CreateJoinOrganizationInvitation.Request", "CreateJoinOrganizationInvitation.Response"
]

INVITATION_EXPIRATION_DAYS = 3


class CreateJoinOrganizationInvitation(ICreateJoinOrganizationInvitation):
    def __init__(
        self,
        db: MongoDbDep,
        logger: LoggerDep,
        user_context: UserContextDep,
    ) -> None:
        self._invitation_collection = db.get_collection(CollectionName.JOIN_ORGANIZATION_INVITATIONS)
        self._logger = logger
        self._user_context = user_context
        self._organization_collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._user_collection = db.get_collection(CollectionName.USERS)

    class Request(p.BaseModel):
        user_id: PyObjectUUID

    class Response(p.BaseModel):
        invitation: JoinOrganizationInvitationModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        receiver_id = request.user_id
        organization_id = self._user_context.organization_id
        sender_id = self._user_context.user_id

        # check if the invitation sender is the owner of the organization
        organization_data = self._organization_collection.find_one({"_id": organization_id, "owner_id": sender_id})
        if not organization_data:
            self._logger.error(f"User with id {sender_id}) has no permission to send invitation.")
            raise BadRequestError("User has no permission to send invitation.")

        # check if receiver is a valid user in database
        user_data = self._user_collection.find_one({"_id": receiver_id})
        if not user_data:
            self._logger.error(f"User with id {receiver_id} is not found.")
            raise BadRequestError("User is not found.")

        # process create an invitation
        expires_at = get_utc_now() + timedelta(days=INVITATION_EXPIRATION_DAYS)

        invitation = JoinOrganizationInvitationModel(
            organization_id=organization_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            taken_action=None,
            expires_at=expires_at,
        )
        invitation_data = invitation.model_dump(by_alias=True)
        inserted_invitation = self._invitation_collection.insert_one(invitation_data)
        created_invitation = self._invitation_collection.find_one({"_id": inserted_invitation.inserted_id})
        if not created_invitation:
            self._logger.error(
                f"Insert join_organization_invitation data with id {inserted_invitation.inserted_id} successfully, but unable to find the created join organization_invitation"
            )
            raise InternalServerError(
                "Insert join_rganization_invitation data successfully, but unable to find the created join organization_invitation"
            )

        created_invitation = JoinOrganizationInvitationModel(**created_invitation)
        return self.Response(invitation=created_invitation)


CreateJoinOrganizationInvitationDep = t.Annotated[CreateJoinOrganizationInvitation, Depends()]
