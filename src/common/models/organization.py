from enum import Enum
from typing import Optional

import pydantic as p

from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete, PyObjectUUID


class OrganizationModel(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete):
    name: str = p.Field(alias="name")
    avatar_url: str | None = p.Field(default=None, alias="avatar_url")
    owner_id: PyObjectUUID = p.Field(alias="owner_id")
    is_default: bool = p.Field(default=False, alias="is_default")
