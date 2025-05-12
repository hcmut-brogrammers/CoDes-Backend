import typing as t

import pydantic as p

from .line import AbstractLineModel
from .shape import ShapeModel, ShapeType


class BaseArrowModel(AbstractLineModel, p.BaseModel):
    shapeType: t.Literal[ShapeType.Arrow] = p.Field(default=ShapeType.Arrow, alias="shapeType")
    # extra properties for Arrow
    points: list[float] = p.Field(default=[], alias="points")
    tension: float | None = p.Field(default=None, alias="tension")
    closed: bool | None = p.Field(default=None, alias="closed")
    pointerLength: float | None = p.Field(default=None, alias="pointerLength")
    pointerWidth: float | None = p.Field(default=None, alias="pointerWidth")
    pointerAtBeginning: bool | None = p.Field(default=None, alias="pointerAtBeginning")
    pointerAtEnding: bool | None = p.Field(default=None, alias="pointerAtEnding")


class ArrowModel(BaseArrowModel, ShapeModel):
    pass
