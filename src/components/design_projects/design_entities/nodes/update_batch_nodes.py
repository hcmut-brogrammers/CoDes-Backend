import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends
from pymongo import UpdateOne

from src.common.design_entities.composite_type_for_model import ShapeElementModel
from src.common.models.base import BaseMetaTimeModel, BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete
from src.common.models.design_entities.shape import ShapeModel
from src.components.design_projects.design_entities.nodes.create_node import CreateNode
from src.components.design_projects.design_entities.nodes.update_node import UpdateNode
from src.components.design_projects.design_entities.shapes.create_shape import CreateShape

from .....common.auth.user_context import UserContextDep
from .....common.design_entities.type import GlobalCompositeOperationType, HTMLImageElement, ShapeType, Vector2d
from .....common.models import DesignProjectModel
from .....common.models.design_entities.node import NodeModel
from .....constants.mongo import CollectionName
from .....dependencies import LoggerDep, MongoDbDep
from .....exceptions import BadRequestError, InternalServerError
from .....interfaces.base_component import IBaseComponent
from .....utils.logger import execute_service_method

IUpdateBatchNodes = IBaseComponent["UpdateBatchNodes.Request", "UpdateBatchNodes.Response"]


class UpdateBatchNodes(IUpdateBatchNodes):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context

    # [?] mấy fields create_at,... trong baseClass BaseMdelWithDateTime có bắt buộc phải có không?
    # hiện tại đang set mấy field đó optional ~ có thể bằng None
    class BaseHttpRequest:
        nodes: list[UpdateNode.HttpRequest]

    class HttpRequest(BaseHttpRequest, p.BaseModel):
        pass

    class Request(BaseHttpRequest, p.BaseModel):
        project_id: UUID

    class Response(p.BaseModel):
        success: bool = True
        error_message: str | None = None
        updated_nodes: ShapeElementModel | None = None

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        project_id = request.project_id
        organization_id = self._user_context.organization_id

        # before process
        is_project_exist = self._collection.count_documents(
            {"_id": project_id, "organization_id": organization_id}, limit=1
        )
        if is_project_exist <= 0:
            log_message = f"Project with id {project_id} not found."
            error_message = f"Project not found."
            self._logger.error(log_message)
            raise BadRequestError(error_message)

        # create bulk operations
        bulk_operations = []
        for node in request.nodes:
            node_id = node.node_id
            update_data = node.model_dump(exclude={"node_id"}, exclude_none=True)

            bulk_operations.append(
                UpdateOne(
                    {"_id": project_id, "nodes._id": node_id},
                    {"$set": {"nodes.$": {"_id": node_id, **update_data}}},
                )
            )

        if not bulk_operations:
            return self.Response(success=False, error_message="No update operations provided.")

        # process bulk update operations
        try:
            result = self._collection.bulk_write(bulk_operations, ordered=False)
            ## log bulk result data
            # self._logger.info(result.bulk_api_result)
        except Exception as e:
            self._logger.error(f"Bulk update failed: {e}")
            return self.Response(success=False, error_message="Bulk update failed.")

        # process response
        return self.Response(success=True, error_message=None, updated_nodes=None)


UpdateBatchNodesDep = t.Annotated[UpdateBatchNodes, Depends()]
