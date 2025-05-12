import typing as t

import pydantic as p

from .shape import BaseShapeModel, ShapeModel, ShapeType


class BaseStarModel(BaseShapeModel, p.BaseModel):
    shapeType: t.Literal[ShapeType.Star] = p.Field(default=ShapeType.Star, alias="shapeType")
    # extra properties for Star
    numPoints: int = p.Field(alias="numPoints")
    innerRadius: float = p.Field(alias="innerRadius")
    outerRadius: float = p.Field(alias="outerRadius")


class StarModel(BaseStarModel, ShapeModel):
    pass
