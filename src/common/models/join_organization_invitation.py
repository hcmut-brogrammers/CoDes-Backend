from enum import Enum

import pydantic as p

from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete, PyObjectDatetime, PyObjectUUID


class InvitationStatus(str, Enum):
    Pending = "Pending"
    Completed = "Completed"


class InviteeAction(str, Enum):
    Accept = "Accept"
    Reject = "Reject"


class TakenAction(p.BaseModel):
    action: InviteeAction = p.Field(alias="action")
    taken_at: PyObjectDatetime = p.Field(alias="taken_at")


class JoinOrganizationInvitationModel(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete):
    organization_id: PyObjectUUID = p.Field(alias="organization_id")
    sender_id: PyObjectUUID = p.Field(alias="sender_id")
    receiver_id: PyObjectUUID = p.Field(alias="receiver_id")
    status: InvitationStatus = p.Field(alias="status", default=InvitationStatus.Pending)
    taken_action: TakenAction | None = p.Field(alias="taken_action", default=None)
    expires_at: PyObjectDatetime = p.Field(alias="expires_at")
    is_read: bool = p.Field(alias="is_read", default=False)
