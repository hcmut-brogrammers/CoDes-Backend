from enum import Enum

import pydantic as p

from ...utils.common import get_utc_now
from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete, PyObjectDatetime, PyObjectUUID


class UserRole(str, Enum):
    OrganizationAdmin = "OrganizationAdmin"
    OrganizationMember = "OrganizationMember"


class JoinedOrganization(p.BaseModel):
    organization_id: PyObjectUUID = p.Field(alias="organization_id")
    role: UserRole = p.Field(alias="role", default=UserRole.OrganizationMember)
    joined_at: PyObjectDatetime = p.Field(alias="joined_at", default_factory=get_utc_now)


class UserModel(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete):
    username: str = p.Field(alias="username")
    email: str = p.Field(alias="email")
    hashed_password: str = p.Field(alias="hashed_password")
    # TODO: to be removed
    role: UserRole = p.Field(alias="role", default=UserRole.OrganizationMember)
    joined_organizations: list[JoinedOrganization] = p.Field(alias="joined_organizations", default=[])
