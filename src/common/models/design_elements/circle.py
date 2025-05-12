import typing as t

import pydantic as p

from .shape import BaseShapeModel, ShapeModel, ShapeType


class BaseCircleModel(BaseShapeModel, p.BaseModel):
    shapeType: t.Literal[ShapeType.Circle] = p.Field(default=ShapeType.Circle, alias="shapeType")
    radius: float | None = p.Field(default=None, alias="radius")


class CircleModel(BaseCircleModel, ShapeModel):
    pass
