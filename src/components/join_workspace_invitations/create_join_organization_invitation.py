import typing as t
from datetime import timedelta
from uuid import UUID

import pydantic as p
from fastapi import Depends
from pymongo.cursor import Cursor

from src.utils.common import get_utc_now

from ...common.models import JoinOrganizationInvitationModel, Status
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import InternalServerError
from ...interfaces.base_component import IBaseComponent
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
        self._organization_collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._invitation_collection = db.get_collection(CollectionName.JOIN_ORGANIZATION_INVITATIONS)
        self._logger = logger
        self._user_context = user_context

    class Request(p.BaseModel):
        user_id: UUID

    class Response(p.BaseModel):
        invitation: JoinOrganizationInvitationModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        receiver_id = request.user_id
        organization_id = self._user_context.organization_id
        sender_id = self._user_context.user_id

        ## [?] check if receiver is a valid user in database
        # TODO: Implement

        ## [?] check if the receiver has been already joined the organization of the sender_id
        # TODO: Implement

        # process create an invitation
        taken_at = get_utc_now()
        expires_at = taken_at + timedelta(days=INVITATION_EXPIRATION_DAYS)

        invitation = JoinOrganizationInvitationModel(
            organization_id=organization_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            taken_at=taken_at,
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
                "Insert join _rganization_invitation data successfully, but unable to find the created join organization_invitation"
            )

        created_invitation = JoinOrganizationInvitationModel(**created_invitation)
        return self.Response(invitation=created_invitation)


CreateJoinOrganizationInvitationDep = t.Annotated[CreateJoinOrganizationInvitation, Depends()]
