import pydantic as p

from .node import BaseNodeModel, NodeModel
from .type import HTMLImageElement, ShapeType, Vector2d


class BaseShapeModel(BaseNodeModel, p.BaseModel):
    # extra properties for Shape
    shapeType: ShapeType | None = p.Field(default=None, alias="shapeType")

    fill: str | None = p.Field(default=None, alias="fill")
    fillPatternImage: HTMLImageElement | None = p.Field(
        default=None, alias="fillPatternImage"
    )  # Representing as URL or image name
    fillPatternX: float | None = p.Field(default=None, alias="fillPatternX")
    fillPatternY: float | None = p.Field(default=None, alias="fillPatternY")
    fillPatternOffset: Vector2d | None = p.Field(default=None, alias="fillPatternOffset")
    fillPatternOffsetX: float | None = p.Field(default=None, alias="fillPatternOffsetX")
    fillPatternOffsetY: float | None = p.Field(default=None, alias="fillPatternOffsetY")
    fillPatternScale: Vector2d | None = p.Field(default=None, alias="fillPatternScale")
    fillPatternScaleX: float | None = p.Field(default=None, alias="fillPatternScaleX")
    fillPatternScaleY: float | None = p.Field(default=None, alias="fillPatternScaleY")
    fillPatternRotation: float | None = p.Field(default=None, alias="fillPatternRotation")
    fillPatternRepeat: str | None = p.Field(default=None, alias="fillPatternRepeat")
    fillLinearGradientStartPoint: Vector2d | None = p.Field(default=None, alias="fillLinearGradientStartPoint")
    fillLinearGradientStartPointX: float | None = p.Field(default=None, alias="fillLinearGradientStartPointX")
    fillLinearGradientStartPointY: float | None = p.Field(default=None, alias="fillLinearGradientStartPointY")
    fillLinearGradientEndPoint: Vector2d | None = p.Field(default=None, alias="fillLinearGradientEndPoint")
    fillLinearGradientEndPointX: float | None = p.Field(default=None, alias="fillLinearGradientEndPointX")
    fillLinearGradientEndPointY: float | None = p.Field(default=None, alias="fillLinearGradientEndPointY")
    fillLinearGradientColorStops: list[str | float] | None = p.Field(default=None, alias="fillLinearGradientColorStops")
    fillRadialGradientStartPoint: Vector2d | None = p.Field(default=None, alias="fillRadialGradientStartPoint")
    fillRadialGradientStartPointX: float | None = p.Field(default=None, alias="fillRadialGradientStartPointX")
    fillRadialGradientStartPointY: float | None = p.Field(default=None, alias="fillRadialGradientStartPointY")
    fillRadialGradientEndPoint: Vector2d | None = p.Field(default=None, alias="fillRadialGradientEndPoint")
    fillRadialGradientEndPointX: float | None = p.Field(default=None, alias="fillRadialGradientEndPointX")
    fillRadialGradientEndPointY: float | None = p.Field(default=None, alias="fillRadialGradientEndPointY")
    fillRadialGradientStartRadius: float | None = p.Field(default=None, alias="fillRadialGradientStartRadius")
    fillRadialGradientEndRadius: float | None = p.Field(default=None, alias="fillRadialGradientEndRadius")
    fillRadialGradientColorStops: list[str | float] | None = p.Field(default=None, alias="fillRadialGradientColorStops")
    fillEnabled: bool | None = p.Field(default=None, alias="fillEnabled")
    fillPriority: str | None = p.Field(default=None, alias="fillPriority")
    fillRule: str | None = p.Field(default=None, alias="fillRule")  # CanvasFillRule # e.g., 'nonzero' or 'evenodd'
    stroke: str | None = p.Field(default=None, alias="stroke")
    strokeWidth: float | None = p.Field(default=None, alias="strokeWidth")
    fillAfterStrokeEnabled: bool | None = p.Field(default=None, alias="fillAfterStrokeEnabled")
    hitStrokeWidth: float | str | None = p.Field(default=None, alias="hitStrokeWidth")
    strokeScaleEnabled: bool | None = p.Field(default=None, alias="strokeScaleEnabled")
    strokeHitEnabled: bool | None = p.Field(default=None, alias="strokeHitEnabled")
    strokeEnabled: bool | None = p.Field(default=None, alias="strokeEnabled")
    lineJoin: str | None = p.Field(default=None, alias="lineJoin")  # LineJoin # "miter" | "round" | "bevel"
    lineCap: str | None = p.Field(default=None, alias="lineCap")  # LineCap # "butt" | "round" | "square"
    # sceneFunc: Callable[[Context, Shape], None]
    # hitFunc: Callable[[Context, Shape], None]
    shadowColor: str | None = p.Field(default=None, alias="shadowColor")
    shadowBlur: float | None = p.Field(default=None, alias="shadowBlur")
    shadowOffset: Vector2d | None = p.Field(default=None, alias="shadowOffset")
    shadowOffsetX: float | None = p.Field(default=None, alias="shadowOffsetX")
    shadowOffsetY: float | None = p.Field(default=None, alias="shadowOffsetY")
    shadowOpacity: float | None = p.Field(default=None, alias="shadowOpacity")
    shadowEnabled: bool | None = p.Field(default=None, alias="shadowEnabled")
    shadowForStrokeEnabled: bool | None = p.Field(default=None, alias="shadowForStrokeEnabled")
    dash: list[float] | None = p.Field(default=None, alias="dash")
    dashOffset: float | None = p.Field(default=None, alias="dashOffset")
    dashEnabled: bool | None = p.Field(default=None, alias="dashEnabled")
    perfectDrawEnabled: bool | None = p.Field(default=None, alias="perfectDrawEnabled")

    model_config = p.ConfigDict(arbitrary_types_allowed=True, use_enum_values=True)


class ShapeModel(BaseShapeModel, NodeModel):
    pass
