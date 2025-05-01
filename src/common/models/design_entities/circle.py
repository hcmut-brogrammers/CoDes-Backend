import pydantic as p

from src.common.models.design_entities.shape import ShapeModel

from ..base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete


class CircleModel(ShapeModel, BaseModelWithSoftDelete, BaseModelWithDateTime, BaseModelWithId):
    # extra properties for Circle
    radius: float | None = p.Field(default=None, alias="radius")
