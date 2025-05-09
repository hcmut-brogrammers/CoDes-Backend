import pydantic as p

from ..base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete
from .shape import ShapeModel


class LineModel(ShapeModel):
    # extra properties for Line
    points: list[float] | None = p.Field(default=None, alias="points")
    tension: float | None = p.Field(default=None, alias="tension")
    closed: bool | None = p.Field(default=None, alias="closed")
    bezier: bool | None = p.Field(default=None, alias="bezier")
