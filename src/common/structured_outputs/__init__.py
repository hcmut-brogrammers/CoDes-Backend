import typing as t

import pydantic as p

from ...common.models import GlobalCompositeOperationType, ShapeType, Vector2d


class ParsedNodeModel(p.BaseModel):
    x: float
    y: float
    width: float
    height: float
    visible: bool
    listening: bool
    name: str
    opacity: float
    scale: Vector2d
    scaleX: float
    skewX: float
    skewY: float
    scaleY: float
    rotation: float
    rotationDeg: float
    offset: Vector2d
    offsetX: float
    offsetY: float
    draggable: bool
    dragDistance: float
    preventDefault: bool
    globalCompositeOperation: GlobalCompositeOperationType


class ParsedShapeModel(ParsedNodeModel, p.BaseModel):
    fill: str
    # fillPatternImage: HTMLImageElement | None = p.Field(
    #     default=None, alias="fillPatternImage"
    # )  # Representing as URL or image name
    fillPatternX: float
    fillPatternY: float
    fillPatternOffset: Vector2d
    fillPatternOffsetX: float
    fillPatternOffsetY: float
    fillPatternScale: Vector2d
    fillPatternScaleX: float
    fillPatternScaleY: float
    fillPatternRotation: float
    fillPatternRepeat: str
    fillLinearGradientStartPoint: Vector2d
    fillLinearGradientStartPointX: float
    fillLinearGradientStartPointY: float
    fillLinearGradientEndPoint: Vector2d
    fillLinearGradientEndPointX: float
    fillLinearGradientEndPointY: float
    fillLinearGradientColorStops: list[str | float]
    fillRadialGradientStartPoint: Vector2d
    fillRadialGradientStartPointX: float
    fillRadialGradientStartPointY: float
    fillRadialGradientEndPoint: Vector2d
    fillRadialGradientEndPointX: float
    fillRadialGradientEndPointY: float
    fillRadialGradientStartRadius: float
    fillRadialGradientEndRadius: float
    fillRadialGradientColorStops: list[str | float]
    fillEnabled: bool
    fillPriority: str
    fillRule: str
    stroke: str
    strokeWidth: float
    fillAfterStrokeEnabled: bool
    hitStrokeWidth: float
    strokeScaleEnabled: bool
    strokeHitEnabled: bool
    strokeEnabled: bool
    lineJoin: str
    lineCap: str
    shadowColor: str
    shadowBlur: float
    shadowOffset: Vector2d
    shadowOffsetX: float
    shadowOffsetY: float
    shadowOpacity: float
    shadowEnabled: bool
    shadowForStrokeEnabled: bool
    dash: list[float]
    dashOffset: float
    dashEnabled: bool
    perfectDrawEnabled: bool


class ParsedCircleModel(ParsedShapeModel, ParsedNodeModel, p.BaseModel):
    shapeType: t.Literal[ShapeType.Circle]
    radius: float | None
