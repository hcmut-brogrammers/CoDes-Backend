import typing as t

import pydantic as p

from .shape import BaseShapeModel, ShapeModel, ShapeType


class AbstractLineModel(BaseShapeModel, p.BaseModel):
    # extra properties for Line
    points: list[float] | None = p.Field(default=None, alias="points")
    tension: float | None = p.Field(default=None, alias="tension")
    closed: bool | None = p.Field(default=None, alias="closed")
    bezier: bool | None = p.Field(default=None, alias="bezier")


class BaseLineModel(AbstractLineModel, p.BaseModel):
    shapeType: t.Literal[ShapeType.Line] = p.Field(default=ShapeType.Line, alias="shapeType")


class LineModel(BaseLineModel, ShapeModel):
    pass
