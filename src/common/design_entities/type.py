from dataclasses import dataclass
from enum import Enum

import pydantic as p

"""------------------------------NodeModel------------------------------"""

# NodeModel is a base class for all nodes in the design project
# ShapeElementModel = ShapeModel | NodeModel


class GlobalCompositeOperationType(str, Enum):
    EMPTY = ""
    SourceOver = "source-over"
    SourceIn = "source-in"
    SourceOut = "source-out"
    SourceAtop = "source-atop"
    DestinationOver = "destination-over"
    DestinationIn = "destination-in"
    DestinationOut = "destination-out"
    DestinationAtop = "destination-atop"
    Lighter = "lighter"
    Copy = "copy"
    Xor = "xor"
    Multiply = "multiply"
    Screen = "screen"
    Overlay = "overlay"
    Darken = "darken"
    Lighten = "lighten"
    ColorDodge = "color-dodge"
    ColorBurn = "color-burn"
    HardLight = "hard-light"
    SoftLight = "soft-light"
    Difference = "difference"
    Exclusion = "exclusion"
    Hue = "hue"
    Saturation = "saturation"
    Color = "color"
    Luminosity = "luminosity"


class Vector2d(p.BaseModel):
    x: float | None = p.Field(alias="x", default=None)
    y: float | None = p.Field(alias="y", default=None)


"""------------------------------ShapeModel------------------------------"""


class HTMLImageElement(p.BaseModel):
    # src: PyObjectHttpUrlStr | None = p.Field(alias="src", default=None)
    src: str | None = p.Field(alias="src", default=None)
    alt: str | None = p.Field(alias="alt", default=None)
    width: int | None = p.Field(alias="width", default=None)
    height: int | None = p.Field(alias="height", default=None)
    naturalWidth: int | None = p.Field(alias="naturalWidth", default=None)
    naturalHeight: int | None = p.Field(alias="naturalHeight", default=None)
    complete: bool | None = p.Field(alias="complete", default=None)
    crossOrigin: str | None = p.Field(alias="crossOrigin", default=None)
    # https://developer.mozilla.org/en-US/docs/Web/API/HTMLImageElement


class ShapeType(str, Enum):
    Circle = "Circle"
    Rect = "Rect"
    RegularPolygon = "Regular-Polygon"
    Line = "Line"
    Text = "Text"
    Image = "Image"
