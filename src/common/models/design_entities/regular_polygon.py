import pydantic as p

from src.common.models.design_entities.shape import ShapeModel

from ..base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete


class RegularPolygonModel(ShapeModel, BaseModelWithSoftDelete, BaseModelWithDateTime, BaseModelWithId):
    # extra properties for Regular-Polygon
    sides: int | None = p.Field(default=None, alias="sides")
    radius: float | None = p.Field(default=None, alias="radius")
