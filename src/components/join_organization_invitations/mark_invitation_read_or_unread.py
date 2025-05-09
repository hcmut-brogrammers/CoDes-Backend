import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import JoinOrganizationInvitationModel, PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...interfaces import IBaseComponent
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method
from ..organizations import GetOrganizationByIdDep
from ..users import GetUserByIdDep

IMarkInvitationReadOrUnread = IBaseComponent[
    "MarkInvitationReadOrUnread.Request", "MarkInvitationReadOrUnread.Response"
]

INVITATION_EXPIRATION_DAYS = 3


class MarkInvitationReadOrUnread(IMarkInvitationReadOrUnread):
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

    class Request(p.BaseModel):
        invitation_id: PyObjectUUID
        is_read: bool

    class Response(p.BaseModel):
        success: bool

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        receiver_id = self._user_context.user_id
        invitation_id = request.invitation_id
        is_read = request.is_read

        query = {
            "_id": invitation_id,
        }
        invitation_data = self._collection.find_one(query)
        if not invitation_data:
            self._logger.error(f"Invitation with id {invitation_id} not found.")
            return self.Response(success=False)

        invitation = JoinOrganizationInvitationModel(**invitation_data)
        if invitation.receiver_id != receiver_id:
            self._logger.error(f"Invitation with id {invitation_id} does not belong to user {receiver_id}.")
            return self.Response(success=False)

        invitation.is_read = is_read
        invitation.updated_at = get_utc_now()
        update_result = self._collection.update_one(query, {"$set": invitation.model_dump(exclude={"id"})})
        if not update_result.modified_count:
            self._logger.error(f"Failed to mark invitation is_read {is_read} with id {invitation_id}.")
            return self.Response(success=False)

        return self.Response(success=True)


MarkInvitationReadOrUnreadDep = t.Annotated[MarkInvitationReadOrUnread, Depends()]
