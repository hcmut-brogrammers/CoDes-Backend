import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from .....common.auth.user_context import UserContextDep
from .....common.design_entities.type import GlobalCompositeOperationType, Vector2d
from .....common.models import DesignProjectModel
from .....common.models.design_entities.node import NodeModel
from .....constants.mongo import CollectionName
from .....dependencies import LoggerDep, MongoDbDep
from .....exceptions import BadRequestError
from .....interfaces.base_component import IBaseComponent
from .....utils.logger import execute_service_method

ICreateNode = IBaseComponent["CreateNode.Request", "CreateNode.Response"]


class CreateNode(ICreateNode):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context

    class BaseHttpRequest:
        x: float | None = p.Field(default=None)
        y: float | None = p.Field(default=None)
        width: float | None = p.Field(default=None)
        height: float | None = p.Field(default=None)
        visible: bool | None = p.Field(default=None)
        listening: bool | None = p.Field(default=None)
        name: str | None = p.Field(default=None)
        opacity: float | None = p.Field(default=None)
        scale: Vector2d | None = p.Field(default=None)
        scaleX: float | None = p.Field(default=None)
        skewX: float | None = p.Field(default=None)
        skewY: float | None = p.Field(default=None)
        scaleY: float | None = p.Field(default=None)
        rotation: float | None = p.Field(default=None)
        rotationDeg: float | None = p.Field(default=None)
        offset: Vector2d | None = p.Field(default=None)
        offsetX: float | None = p.Field(default=None)
        offsetY: float | None = p.Field(default=None)
        draggable: bool | None = p.Field(default=None)
        dragDistance: float | None = p.Field(default=None)
        preventDefault: bool | None = p.Field(default=None)
        globalCompositeOperation: GlobalCompositeOperationType | None = p.Field(default=None)

    class HttpRequest(BaseHttpRequest, p.BaseModel):
        pass

    class Request(BaseHttpRequest, p.BaseModel):
        project_id: UUID

    class Response(p.BaseModel):
        created_node: NodeModel

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

        # process create organization
        create_data = request.model_dump(by_alias=True, exclude={"project_id"}, exclude_none=True)
        node = NodeModel(**create_data)

        # current_project.nodes.append(node)
        current_project.nodes.insert(0, node)
        self._collection.update_one(
            {"_id": project_id}, {"$set": current_project.model_dump(exclude={"id"}, exclude_none=True)}
        )

        return self.Response(created_node=node)


CreateNodeDep = t.Annotated[CreateNode, Depends()]
