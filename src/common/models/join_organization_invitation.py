from enum import Enum
from typing import Optional

import pydantic as p

from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete, PyObjectDatetime, PyObjectUUID


class Status(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class InviteeAction(str, Enum):
    accept = "accept"
    reject = "reject"


class JoinOrganizationInvitationModel(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete):
    organization_id: PyObjectUUID = p.Field(alias="organization_id")
    sender_id: PyObjectUUID = p.Field(alias="sender_id")
    receiver_id: PyObjectUUID = p.Field(alias="receiver_id")
    status: Status = p.Field(alias="status", default=Status.pending)
    taken_action: InviteeAction | None = p.Field(alias="taken_action", default=None)
    taken_at: PyObjectDatetime = p.Field(alias="taken_at")
    expires_at: PyObjectDatetime = p.Field(alias="expires_at")
