from typing import Union

import pydantic as p

from src.common.design_entities.type import Vector2d
from src.common.models.base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete
from src.common.models.design_entities.node import NodeModel


class ShapeModel(NodeModel, BaseModelWithSoftDelete, BaseModelWithDateTime, BaseModelWithId):
    fill: str | None = p.Field(default=None, alias="fill")
    # fillPatternImage: HTMLImageElement
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
    fillRule: str | None = p.Field(default=None, alias="fillRule")  # CanvasFillRule
    stroke: str | None = p.Field(default=None, alias="stroke")
    strokeWidth: float | None = p.Field(default=None, alias="strokeWidth")
    fillAfterStrokeEnabled: bool | None = p.Field(default=None, alias="fillAfterStrokeEnabled")
    hitStrokeWidth: float | str | None = p.Field(default=None, alias="hitStrokeWidth")
    strokeScaleEnabled: bool | None = p.Field(default=None, alias="strokeScaleEnabled")
    strokeHitEnabled: bool | None = p.Field(default=None, alias="strokeHitEnabled")
    strokeEnabled: bool | None = p.Field(default=None, alias="strokeEnabled")
    lineJoin: str | None = p.Field(default=None, alias="lineJoin")  # LineJoin
    lineCap: str | None = p.Field(default=None, alias="lineCap")  # LineCap
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
