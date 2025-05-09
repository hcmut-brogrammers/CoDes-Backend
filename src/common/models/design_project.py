import pydantic as p

from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete, PyObjectUUID
from .design_elements import ShapeElementModel


class DesignProjectModel(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete):
    name: str = p.Field(alias="name")
    thumbnail_url: str | None = p.Field(default=None, alias="thumbnail_url")
    organization_id: PyObjectUUID = p.Field(alias="organization_id")
    owner_id: PyObjectUUID = p.Field(alias="owner_id")
    elements: list[ShapeElementModel] = p.Field(default=[], alias="elements")
