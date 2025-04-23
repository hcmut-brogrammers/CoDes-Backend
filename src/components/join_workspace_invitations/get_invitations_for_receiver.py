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
from ...interfaces.base_component import IBaseComponentWithoutRequest
from ...utils.logger import execute_service_method

IGetInvitationsForReceiver = IBaseComponentWithoutRequest["GetInvitationsForReceiver.Response"]

INVITATION_EXPIRATION_DAYS = 3


class GetInvitationsForReceiver(IGetInvitationsForReceiver):
    def __init__(
        self,
        db: MongoDbDep,
        logger: LoggerDep,
        user_context: UserContextDep,
    ) -> None:
        self._invitation_collection = db.get_collection(CollectionName.JOIN_ORGANIZATION_INVITATIONS)
        self._logger = logger
        self._user_context = user_context

    class Response(p.BaseModel):
        invitations: t.List[JoinOrganizationInvitationModel]

    async def aexecute(self) -> "Response":
        self._logger.info(execute_service_method(self))

        receiver_id = self._user_context.user_id

        filter = {"receiver_id": receiver_id, "taken_action": None, "expires_at": {"$gt": get_utc_now()}}

        invitations_data = self._invitation_collection.find(filter)
        # if not invitations_data:
        #     self._logger.error(f"No join_organization_invitation data with id {receiver_id} is found")
        #     raise InternalServerError("Insert join_rganization_invitation data is found")

        invitations = [JoinOrganizationInvitationModel(**invitation_data) for invitation_data in invitations_data]
        return self.Response(invitations=invitations)


GetInvitationsForReceiverDep = t.Annotated[GetInvitationsForReceiver, Depends()]
