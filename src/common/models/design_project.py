import typing as t
from enum import Enum

import pydantic as p

from ...common.models.design_entities.node import NodeModel
from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete, PyObjectUUID


class DesignProjectModel(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete):
    name: str = p.Field(alias="name")
    thumbnail_url: str | None = p.Field(default=None, alias="thumbnail_url")
    organization_id: PyObjectUUID = p.Field(alias="organization_id")
    owner_id: PyObjectUUID = p.Field(alias="owner_id")
    nodes: list[NodeModel] = p.Field(default=[], alias="nodes")
