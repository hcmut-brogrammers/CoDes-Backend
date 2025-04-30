from dataclasses import dataclass
from enum import Enum

import pydantic as p


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


# @dataclass
class Vector2d(p.BaseModel):
    x: float | None = p.Field(alias="x", default=None)
    y: float | None = p.Field(alias="y", default=None)


class HTMLImageElement(p.BaseModel):
    src: PyObjectHttpUrlStr | None = p(alias="src", default=None)
    alt: str | None = p(alias="alt", default=None)
    width: int | None = p(alias="width", default=None)
    height: int | None = p(alias="height", default=None)
    naturalWidth: int | None = p(alias="naturalWidth", default=None)
    naturalHeight: int | None = p(alias="naturalHeight", default=None)
    complete: bool | None = p(alias="complete", default=None)
    crossOrigin: str | None = p(alias="crossOrigin", default=None)
