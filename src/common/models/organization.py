import pydantic as p

from ...utils.common import get_utc_now
from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete, PyObjectDatetime, PyObjectUUID
from .user import UserRole


class JoinOrganizationMember(p.BaseModel):
    member_id: PyObjectUUID = p.Field(alias="member_id")
    member_role: UserRole = p.Field(alias="member_role", default=UserRole.OrganizationMember)
    joined_at: PyObjectDatetime = p.Field(alias="joined_at", default_factory=get_utc_now)


class OrganizationModel(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete):
    name: str = p.Field(alias="name")
    avatar_url: str | None = p.Field(default=None, alias="avatar_url")
    owner_id: PyObjectUUID = p.Field(alias="owner_id")
    is_default: bool = p.Field(default=False, alias="is_default")
    members: list[JoinOrganizationMember] = p.Field(alias="members", default=[])
