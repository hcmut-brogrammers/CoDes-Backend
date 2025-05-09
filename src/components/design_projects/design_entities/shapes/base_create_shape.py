import typing as t

import pydantic as p
from fastapi import Depends

from .....common.models import DesignProjectModel, HTMLImageElement, PyObjectUUID, ShapeType, Vector2d
from .....common.models.design_elements.shape import ShapeModel
from .....constants.mongo import CollectionName
from .....dependencies import LoggerDep, MongoDbDep
from .....exceptions import BadRequestError
from .....interfaces import IBaseComponent
from .....utils.logger import execute_service_method
from ..nodes.create_node import CreateNode

IBaseCreateShape = IBaseComponent["BaseCreateShape.Request", "BaseCreateShape.Response"]


class BaseCreateShape(IBaseCreateShape):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger

    class BaseHttpRequest(CreateNode.BaseHttpRequest):
        shapeType: ShapeType | None = p.Field(default=None)
        fill: str | None = p.Field(default=None)
        fillPatternImage: HTMLImageElement | None = p.Field(default=None)  # Representing as URL or image name
        fillPatternX: float | None = p.Field(default=None)
        fillPatternY: float | None = p.Field(default=None)
        fillPatternOffset: Vector2d | None = p.Field(default=None)
        fillPatternOffsetX: float | None = p.Field(default=None)
        fillPatternOffsetY: float | None = p.Field(default=None)
        fillPatternScale: Vector2d | None = p.Field(default=None)
        fillPatternScaleX: float | None = p.Field(default=None)
        fillPatternScaleY: float | None = p.Field(default=None)
        fillPatternRotation: float | None = p.Field(default=None)
        fillPatternRepeat: str | None = p.Field(default=None)
        fillLinearGradientStartPoint: Vector2d | None = p.Field(default=None)
        fillLinearGradientStartPointX: float | None = p.Field(default=None)
        fillLinearGradientStartPointY: float | None = p.Field(default=None)
        fillLinearGradientEndPoint: Vector2d | None = p.Field(default=None)
        fillLinearGradientEndPointX: float | None = p.Field(default=None)
        fillLinearGradientEndPointY: float | None = p.Field(default=None)
        fillLinearGradientColorStops: list[str | float] | None = p.Field(default=None)
        fillRadialGradientStartPoint: Vector2d | None = p.Field(default=None)
        fillRadialGradientStartPointX: float | None = p.Field(default=None)
        fillRadialGradientStartPointY: float | None = p.Field(default=None)
        fillRadialGradientEndPoint: Vector2d | None = p.Field(default=None)
        fillRadialGradientEndPointX: float | None = p.Field(default=None)
        fillRadialGradientEndPointY: float | None = p.Field(default=None)
        fillRadialGradientStartRadius: float | None = p.Field(default=None)
        fillRadialGradientEndRadius: float | None = p.Field(default=None)
        fillRadialGradientColorStops: list[str | float] | None = p.Field(default=None)
        fillEnabled: bool | None = p.Field(default=None)
        fillPriority: str | None = p.Field(default=None)
        fillRule: str | None = p.Field(default=None)  # CanvasFillRule # e.g., 'nonzero' or 'evenodd'
        stroke: str | None = p.Field(default=None)
        strokeWidth: float | None = p.Field(default=None)
        fillAfterStrokeEnabled: bool | None = p.Field(default=None)
        hitStrokeWidth: float | str | None = p.Field(default=None)
        strokeScaleEnabled: bool | None = p.Field(default=None)
        strokeHitEnabled: bool | None = p.Field(default=None)
        strokeEnabled: bool | None = p.Field(default=None)
        lineJoin: str | None = p.Field(default=None)  # LineJoin # "miter" | "round" | "bevel"
        lineCap: str | None = p.Field(default=None)  # LineCap # "butt" | "round" | "square"
        shadowColor: str | None = p.Field(default=None)
        shadowBlur: float | None = p.Field(default=None)
        shadowOffset: Vector2d | None = p.Field(default=None)
        shadowOffsetX: float | None = p.Field(default=None)
        shadowOffsetY: float | None = p.Field(default=None)
        shadowOpacity: float | None = p.Field(default=None)
        shadowEnabled: bool | None = p.Field(default=None)
        shadowForStrokeEnabled: bool | None = p.Field(default=None)
        dash: list[float] | None = p.Field(default=None)
        dashOffset: float | None = p.Field(default=None)
        dashEnabled: bool | None = p.Field(default=None)
        perfectDrawEnabled: bool | None = p.Field(default=None)

    class Shape(BaseHttpRequest, p.BaseModel):
        pass

    class HttpRequest(p.BaseModel):
        shape: "BaseCreateShape.Shape"

    class Request(HttpRequest, p.BaseModel):
        design_project_id: PyObjectUUID
        organization_id: PyObjectUUID

    class Response(p.BaseModel):
        created_shape: ShapeModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        design_project_id = request.design_project_id
        organization_id = request.organization_id

        design_project_data = self._collection.find_one({"_id": design_project_id})
        if not design_project_data:
            log_message = f"Design project with id {design_project_id} not found."
            error_message = f"Design project not found."
            self._logger.error(log_message)
            raise BadRequestError(error_message)

        design_project = DesignProjectModel(**design_project_data)
        if design_project.organization_id != organization_id:
            log_message = f"User have no permission to access the design project {design_project_id}."
            error_message = f"User have no permission to access the design project."
            self._logger.error(log_message)
            raise BadRequestError(error_message)

        shape = ShapeModel(**request.shape.model_dump())
        self._collection.update_one(
            {"_id": design_project_id},
            {
                "$push": {
                    "elements": {
                        "$each": [shape.model_dump(by_alias=True, exclude_none=True)],
                        "$position": 0,
                    }
                }
            },
        )
        return self.Response(created_shape=shape)


BaseCreateShapeDep = t.Annotated[BaseCreateShape, Depends()]
