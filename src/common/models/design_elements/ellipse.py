import typing as t

import pydantic as p

from .shape import BaseShapeModel, ShapeModel, ShapeType


class BaseEllipseModel(BaseShapeModel, p.BaseModel):
    shapeType: t.Literal[ShapeType.Ellipse] = p.Field(default=ShapeType.Ellipse, alias="shapeType")
    # extra properties for Ellipse
    radiusX: float = p.Field(alias="radiusX")
    radiusY: float = p.Field(alias="radiusY")


class EllipseModel(BaseEllipseModel, ShapeModel):
    pass
