import typing as t

import pydantic as p

from .shape import BaseShapeModel, ShapeModel, ShapeType


class BaseRectangleModel(BaseShapeModel, p.BaseModel):
    shapeType: t.Literal[ShapeType.Rectangle] = p.Field(default=ShapeType.Rectangle, alias="shapeType")
    cornerRadius: float | list[float] | None = p.Field(default=None, alias="cornerRadius")


class RectangleModel(BaseRectangleModel, ShapeModel):
    pass
