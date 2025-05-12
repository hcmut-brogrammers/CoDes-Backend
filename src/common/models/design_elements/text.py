import typing as t

import pydantic as p

from .shape import BaseShapeModel, ShapeModel, ShapeType


class BaseTextModel(BaseShapeModel, p.BaseModel):
    shapeType: t.Literal[ShapeType.Text] = p.Field(default=ShapeType.Text, alias="shapeType")
    # extra properties for Text
    direction: str | None = p.Field(default=None, alias="direction")
    text: str | None = p.Field(default=None, alias="text")
    fontFamily: str | None = p.Field(default=None, alias="fontFamily")
    fontSize: float | None = p.Field(default=None, alias="fontSize")
    fontStyle: str | None = p.Field(default=None, alias="fontStyle")
    fontVariant: str | None = p.Field(default=None, alias="fontVariant")
    textDecoration: str | None = p.Field(default=None, alias="textDecoration")
    align: str | None = p.Field(default=None, alias="align")
    verticalAlign: str | None = p.Field(default=None, alias="verticalAlign")
    padding: float | list[float] | None = p.Field(default=None, alias="padding")
    lineHeight: float | None = p.Field(default=None, alias="lineHeight")
    letterSpacing: float | None = p.Field(default=None, alias="letterSpacing")
    wrap: str | None = p.Field(default=None, alias="wrap")
    ellipsis: bool | None = p.Field(default=None, alias="ellipsis")


class TextModel(BaseTextModel, ShapeModel):
    pass
