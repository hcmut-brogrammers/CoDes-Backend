import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from .....common.auth.user_context import UserContextDep
from .....common.design_entities.type import HTMLImageElement, ShapeType, Vector2d
from .....common.models import DesignProjectModel
from .....common.models.design_entities.shape import ShapeModel
from .....components.design_projects.design_entities.nodes.create_node import CreateNode
from .....constants.mongo import CollectionName
from .....dependencies import LoggerDep, MongoDbDep
from .....exceptions import BadRequestError
from .....interfaces.base_component import IBaseComponent
from .....utils.logger import execute_service_method

ICreateShape = IBaseComponent["CreateShape.Request", "CreateShape.Response"]


class CreateShape(ICreateShape):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context

    class HttpRequest(CreateNode.HttpRequest):
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
        # sceneFunc: Callable[[Context, Shape], None]
        # hitFunc: Callable[[Context, Shape], None]
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

    class Request(HttpRequest, p.BaseModel):
        project_id: UUID

    class Response(p.BaseModel):
        created_shape: ShapeModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        project_id = request.project_id
        organization_id = self._user_context.organization_id

        # before process
        current_project_data = self._collection.find_one({"_id": project_id})
        if not current_project_data:
            log_message = f"Project with id {project_id} not found."
            error_message = f"Project not found."
            self._logger.error(log_message)
            raise BadRequestError(error_message)

        current_project = DesignProjectModel(**current_project_data)
        if current_project.organization_id != organization_id:
            log_message = f"User have no permission to access the project {project_id}."
            error_message = f"User have no permission to access the project."
            self._logger.error(log_message)
            raise BadRequestError(error_message)

        create_data = request.model_dump(exclude={"project_id"}, exclude_none=True)
        # process create organization
        node = ShapeModel(**create_data)

        # current_project.nodes.append(node)
        current_project.nodes.insert(0, node)
        self._collection.update_one(
            {"_id": project_id}, {"$set": current_project.model_dump(exclude={"id"}, exclude_none=True)}
        )

        return self.Response(created_shape=node)


CreateShapeDep = t.Annotated[CreateShape, Depends()]
