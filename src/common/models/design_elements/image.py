import typing as t

import pydantic as p

from .shape import BaseShapeModel, ShapeModel, ShapeType
from .type import IRect


class BaseImageModel(BaseShapeModel, p.BaseModel):
    shapeType: t.Literal[ShapeType.Image] = p.Field(default=ShapeType.Image, alias="shapeType")
    # extra properties for Image
    image: str = p.Field(alias="image")
    crop: IRect | None = p.Field(default=None, alias="crop")
    cornerRadius: float | list[float] | None = p.Field(default=None, alias="cornerRadius")


class ImageModel(BaseImageModel, ShapeModel):
    pass
