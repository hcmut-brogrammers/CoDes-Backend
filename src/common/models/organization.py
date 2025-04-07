from enum import Enum
from typing import Optional

import pydantic as p

from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete, PyObjectUUID

# class OrganizationRole(str, Enum):
#     OrganizationAdmin = "OrganizationAdmin"
#     OrganizationMember = "OrganizationMember"


class OrganizationModel(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete):
    name: str = p.Field(alias="name", title="organization name", description="The org name")
    avatar_url: Optional[str] = p.Field(
        default=None, alias="avatar_url", title="avatar url", description="The public image url"
    )
    owner_id: PyObjectUUID = p.Field(alias="owner_id", title="owner id", description="The User ID of the org owner")

    # role: OrganizationRole = p.Field(alias="role", default=OrganizationRole.OrganizationMember)
