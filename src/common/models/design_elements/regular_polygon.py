import pydantic as p

from ..base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete
from .shape import ShapeModel


class RegularPolygonModel(ShapeModel):
    # extra properties for Regular-Polygon
    sides: int | None = p.Field(default=None, alias="sides")
    radius: float | None = p.Field(default=None, alias="radius")
