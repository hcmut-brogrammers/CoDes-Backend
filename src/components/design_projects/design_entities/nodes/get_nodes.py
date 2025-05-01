import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from .....common.design_entities.composite_type_for_model import ShapeElementModel
from .....common.models import DesignProjectModel
from .....common.models.design_entities.node import NodeModel
from .....common.models.design_entities.shape import ShapeModel
from .....constants.mongo import CollectionName
from .....dependencies import LoggerDep, MongoDbDep, UserContextDep
from .....exceptions import BadRequestError
from .....interfaces.base_component import IBaseComponent
from .....utils.logger import execute_service_method

IGetNodes = IBaseComponent["GetNodes.Request", "GetNodes.Response"]


class GetNodes(IGetNodes):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context

    class Request(p.BaseModel):
        project_id: UUID

    class Response(p.BaseModel):
        nodes: list[ShapeElementModel]

    async def aexecute(self, request: Request) -> "Response":
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

        nodes = current_project.nodes
        return self.Response(nodes=nodes)


GetNodesDep = t.Annotated[GetNodes, Depends()]
