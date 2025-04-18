from enum import Enum
from typing import Optional

import pydantic as p
from beanie import Document, Indexed, Link, PydanticObjectId

from src.common.models.organization import OrganizationModel
from src.utils.common import generate_uuid

from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete, PyObjectUUID
from .category import CategoryModel


# class ProductModel(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete):
class ProductModel(Document, BaseModelWithDateTime, BaseModelWithSoftDelete):
    # id: PyObjectUUID = p.Field(alias="_id", default_factory=generate_uuid)
    name: str  # You can use normal types just like in pydantic
    organization: Link[OrganizationModel]

    class Settings:
        name = "Product"
