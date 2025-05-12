import typing as t

import pydantic as p

from .shape import BaseShapeModel, ShapeModel, ShapeType


class BaseRingModel(BaseShapeModel, p.BaseModel):
    shapeType: t.Literal[ShapeType.Ring] = p.Field(default=ShapeType.Ring, alias="shapeType")
    # extra properties for Ring
    innerRadius: float = p.Field(alias="innerRadius")
    outerRadius: float = p.Field(alias="outerRadius")


class RingModel(BaseRingModel, ShapeModel):
    pass
