import pydantic as p

from ..base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete
from .type import GlobalCompositeOperationType, Vector2d


class BaseNodeModel(p.BaseModel):
    x: float | None = p.Field(default=None, alias="x")
    y: float | None = p.Field(default=None, alias="y")
    width: float | None = p.Field(default=None, alias="width")
    height: float | None = p.Field(default=None, alias="height")
    visible: bool | None = p.Field(default=None, alias="visible")
    listening: bool | None = p.Field(default=None, alias="listening")
    # _id: str | None = p.Field(default=None, alias="id")
    name: str | None = p.Field(default=None, alias="name")
    opacity: float | None = p.Field(default=None, alias="opacity")
    scale: Vector2d | None = p.Field(default=None, alias="scale")
    scaleX: float | None = p.Field(default=None, alias="scaleX")
    skewX: float | None = p.Field(default=None, alias="skewX")
    skewY: float | None = p.Field(default=None, alias="skewY")
    scaleY: float | None = p.Field(default=None, alias="scaleY")
    rotation: float | None = p.Field(default=None, alias="rotation")
    rotationDeg: float | None = p.Field(default=None, alias="rotationDeg")
    offset: Vector2d | None = p.Field(default=None, alias="offset")
    offsetX: float | None = p.Field(default=None, alias="offsetX")
    offsetY: float | None = p.Field(default=None, alias="offsetY")
    draggable: bool | None = p.Field(default=None, alias="draggable")
    dragDistance: float | None = p.Field(default=None, alias="dragDistance")
    # dragBoundFunc: Callable[[Vector2d], Vector2d] | None = p.Field(default=None, alias="dragBoundFunc")
    preventDefault: bool | None = p.Field(default=None, alias="preventDefault")
    globalCompositeOperation: GlobalCompositeOperationType | None = p.Field(
        default=None, alias="globalCompositeOperation"
    )
    # filters: List[Filter] | None = p.Field(default=None, alias="filters")

    model_config = p.ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class NodeModel(BaseNodeModel, BaseModelWithSoftDelete, BaseModelWithDateTime, BaseModelWithId):
    pass


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
