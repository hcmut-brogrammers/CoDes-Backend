import pydantic as p

from src.common.models.design_entities.shape import ShapeModel

from ..base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete


class LineModel(ShapeModel, BaseModelWithSoftDelete, BaseModelWithDateTime, BaseModelWithId):
    # extra properties for Line
    points: list[float] | None = p.Field(default=None, alias="points")
    tension: float | None = p.Field(default=None, alias="tension")
    closed: bool | None = p.Field(default=None, alias="closed")
    bezier: bool | None = p.Field(default=None, alias="bezier")
