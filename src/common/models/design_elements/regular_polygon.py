import typing as t

import pydantic as p

from .shape import BaseShapeModel, ShapeModel, ShapeType


class BaseRegularPolygonModel(BaseShapeModel, p.BaseModel):
    shapeType: t.Literal[ShapeType.RegularPolygon] = p.Field(default=ShapeType.RegularPolygon, alias="shapeType")
    # extra properties for Regular-Polygon
    sides: int = p.Field(alias="sides")
    radius: float = p.Field(alias="radius")


class RegularPolygonModel(BaseRegularPolygonModel, ShapeModel):
    pass
