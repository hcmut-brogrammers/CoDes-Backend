from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Literal, TypeAlias

# Assuming p is an alias for pydantic
import pydantic as p
from pydantic import BaseModel
from pydantic import Field as pField

# Define GlobalCompositeOperationType as a type alias
GlobalCompositeOperationType: TypeAlias = Literal[
    "",
    "source-over",
    "source-in",
    "source-out",
    "source-atop",
    "destination-over",
    "destination-in",
    "destination-out",
    "destination-atop",
    "lighter",
    "copy",
    "xor",
    "multiply",
    "screen",
    "overlay",
    "darken",
    "lighten",
    "color-dodge",
    "color-burn",
    "hard-light",
    "soft-light",
    "difference",
    "exclusion",
    "hue",
    "saturation",
    "color",
    "luminosity",
]


@dataclass
class Vector2d:
    x: float
    y: float


class Filter:
    pass  # Placeholder for Filter class, implement as needed


class NodeModel(BaseModel):
    x: float | None = pField(default=None, alias="x")
    y: float | None = pField(default=None, alias="y")
    width: float | None = pField(default=None, alias="width")
    height: float | None = pField(default=None, alias="height")
    visible: bool | None = pField(default=None, alias="visible")
    listening: bool | None = pField(default=None, alias="listening")
    # _id: str | None = pField(default=None, alias="id")
    name: str | None = pField(default=None, alias="name")
    opacity: float | None = pField(default=None, alias="opacity")
    scale: Vector2d | None = pField(default=None, alias="scale")
    scaleX: float | None = pField(default=None, alias="scaleX")
    skewX: float | None = pField(default=None, alias="skewX")
    skewY: float | None = pField(default=None, alias="skewY")
    scaleY: float | None = pField(default=None, alias="scaleY")
    rotation: float | None = pField(default=None, alias="rotation")
    rotationDeg: float | None = pField(default=None, alias="rotationDeg")
    offset: Vector2d | None = pField(default=None, alias="offset")
    offsetX: float | None = pField(default=None, alias="offsetX")
    offsetY: float | None = pField(default=None, alias="offsetY")
    draggable: bool | None = pField(default=None, alias="draggable")
    dragDistance: float | None = pField(default=None, alias="dragDistance")
    dragBoundFunc: Callable[[Vector2d], Vector2d] | None = pField(default=None, alias="dragBoundFunc")
    preventDefault: bool | None = pField(default=None, alias="preventDefault")
    globalCompositeOperation: GlobalCompositeOperationType | None = pField(
        default=None, alias="globalCompositeOperation"
    )
    filters: List[Filter] | None = pField(default=None, alias="filters")

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


# https://github.com/konvajs/konva/blob/master/src/Node.ts#L18
# https://developer.mozilla.org/en-US/docs/Web/API/ImageData#instance_properties

# export type Filter = (this: Node, imageData: ImageData) => void;

# Instance properties
# ImageData.data Read only
# A Uint8ClampedArray representing a one-dimensional array containing the data in the RGBA order, with integer values between 0 and 255 (inclusive). The order goes by rows from the top-left pixel to the bottom-right.

# ImageData.colorSpace Read only
# A string indicating the color space of the image data.

# ImageData.height Read only
# An unsigned long representing the actual height, in pixels, of the ImageData.

# ImageData.width Read only
# An unsigned long representing the actual width, in pixels, of the ImageData.
