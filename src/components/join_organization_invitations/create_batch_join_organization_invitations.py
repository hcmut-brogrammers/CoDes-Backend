import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends
from pymongo.cursor import Cursor

from ...common.models import JoinOrganizationInvitationModel, OrganizationModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import BadRequestError, InternalServerError
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method
from .create_join_organization_invitation import CreateJoinOrganizationInvitationDep

ICreateBatchJoinOrganizationInvitation = IBaseComponent[
    "CreateBatchJoinOrganizationInvitation.Request", "CreateBatchJoinOrganizationInvitation.Response"
]


class CreateBatchJoinOrganizationInvitation(ICreateBatchJoinOrganizationInvitation):
    def __init__(
        self,
        db: MongoDbDep,
        logger: LoggerDep,
        user_context: UserContextDep,
        create_invitation: CreateJoinOrganizationInvitationDep,
    ) -> None:
        self._organization_collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger
        self._user_context = user_context
        self._create_invitation = create_invitation

    class Request(p.BaseModel):
        user_ids: t.List["UUID"]

    class Response(p.BaseModel):
        invitations: t.List["JoinOrganizationInvitationModel"]

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        receiver_ids = request.user_ids
        organization_id = self._user_context.organization_id
        sender_id = self._user_context.user_id

        # check if the invitation sender is the owner of the organization
        filter = {
            "_id": organization_id,
            "owner_id": sender_id,
        }
        organization_data = self._organization_collection.find_one(filter)

        if organization_data is None:
            log_message = f"Can not create workspace invitation(s). user with id={sender_id} is not the owner of the organizaton with id={organization_id}"
            error_message = f"Can not create workspace invitation(s). user is not the owner of the organizaton with id"
            self._logger.error(log_message)
            raise BadRequestError(error_message)

        # process create multi invitations
        invitation_responses = [
            await self._create_invitation.aexecute(CreateJoinOrganizationInvitationDep.Request(user_id=user_id))
            for user_id in receiver_ids
        ]
        return self.Response(invitations=list(map(lambda response: response.invitation, invitation_responses)))


CreateBatchJoinOrganizationInvitationDep = t.Annotated[CreateBatchJoinOrganizationInvitation, Depends()]
