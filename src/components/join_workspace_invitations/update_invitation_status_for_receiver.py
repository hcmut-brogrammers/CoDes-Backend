import typing as t
from datetime import timedelta
from uuid import UUID

import pydantic as p
from fastapi import Depends
from pymongo.cursor import Cursor

from src.utils.common import get_utc_now

from ...common.models import InviteeAction, JoinOrganizationInvitationModel, Status
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import InternalServerError
from ...interfaces.base_component import IBaseComponent
from ...utils.logger import execute_service_method

IUpdateInvitationStatusForReceiver = IBaseComponent[
    "UpdateInvitationStatusForReceiver.Request", "UpdateInvitationStatusForReceiver.Response"
]

INVITATION_EXPIRATION_DAYS = 3


class UpdateInvitationStatusForReceiver(IUpdateInvitationStatusForReceiver):
    def __init__(
        self,
        db: MongoDbDep,
        logger: LoggerDep,
        user_context: UserContextDep,
    ) -> None:
        self._invitation_collection = db.get_collection(CollectionName.JOIN_ORGANIZATION_INVITATIONS)
        self._logger = logger
        self._user_context = user_context

    class Request(p.BaseModel):
        taken_action: InviteeAction

    class Response(p.BaseModel):
        invitation: JoinOrganizationInvitationModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        receiver_id = self._user_context.user_id
        taken_action = request.taken_action

        filter = {"receiver_id": receiver_id, "expires_at": {"$gt": get_utc_now()}}

        invitation_data = self._invitation_collection.find_one(filter)

        if not invitation_data:
            self._logger.error(f"No join_organization_invitation data with id {receiver_id} is found")
            raise InternalServerError("Insert join_rganization_invitation data is found")

        update_data: t.Dict[str, t.Any] = {"taken_action": request.taken_action}
        if taken_action == InviteeAction.accept:
            update_data["status"] = Status.accepted
        else:
            update_data["status"] = Status.rejected

        updated_invitation = JoinOrganizationInvitationModel(**invitation_data).model_copy(update=update_data)

        update_result = self._invitation_collection.update_one(
            {"_id": receiver_id}, {"$set": updated_invitation.model_dump(exclude={"id"})}
        )

        return self.Response(invitation=updated_invitation)


UpdateInvitationStatusForReceiverDep = t.Annotated[UpdateInvitationStatusForReceiver, Depends()]
