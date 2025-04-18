from enum import Enum
from typing import Optional
from uuid import UUID

import pydantic as p
from beanie import Document, Indexed, Link, PydanticObjectId

from src.common.models.organization import OrganizationModel
from src.common.models.yard import YardModel
from src.utils.common import generate_uuid

from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete, PyObjectUUID


class HouseModel(Document, BaseModelWithDateTime, BaseModelWithSoftDelete):
    # _id: UUID
    # id: PyObjectUUID = p.Field(alias="_id", default_factory=generate_uuid)
    name: str  # You can use normal types just like in pydantic
    yard: Link[YardModel]

    class Settings:
        name = "Houses"
