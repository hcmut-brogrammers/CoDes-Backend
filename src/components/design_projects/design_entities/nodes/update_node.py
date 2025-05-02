import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from src.common.design_entities.composite_type_for_model import ShapeElementModel
from src.common.models.base import BaseMetaTimeModel, BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete
from src.common.models.design_entities.shape import ShapeModel
from src.components.design_projects.design_entities.nodes.create_node import CreateNode
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


def find_index_and_value(x, lst, func):
    for index, value in enumerate(lst):
        if x == func(value):
            return index, value
    return None, None


IUpdateNode = IBaseComponent["UpdateNode.Request", "UpdateNode.Response"]


class UpdateNode(IUpdateNode):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context

    # [?] mấy fields create_at,... trong baseClass BaseMdelWithDateTime có bắt buộc phải có không?
    # hiện tại đang set mấy field đó optional ~ có thể bằng None
    class BaseHttpRequest(BaseMetaTimeModel, CreateNode.BaseHttpRequest):
        node_id: UUID

    class HttpRequest(BaseHttpRequest, p.BaseModel):
        pass

    class Request(BaseHttpRequest, p.BaseModel):
        project_id: UUID

    class Response(p.BaseModel):
        success: bool = True
        error_message: str | None = None
        updated_node: ShapeElementModel | None = None

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        project_id = request.project_id
        organization_id = self._user_context.organization_id

        # before process
        # check if project exist and user have permission to access the project
        # [?] nên tách ra query riêng 2 trường hợp để check tuần tự, hay gộp chung check 1 lần
        is_project_exist = self._collection.count_documents(
            {"_id": project_id, "organization_id": organization_id}, limit=1
        )
        if is_project_exist <= 0:
            log_message = f"Project with id {project_id} not found."
            error_message = f"Project not found."
            self._logger.error(log_message)
            raise BadRequestError(error_message)

        # # current_project = DesignProjectModel(**current_project_data)
        # if current_project.organization_id != organization_id:
        #     log_message = f"User have no permission to access the project {project_id}."
        #     error_message = f"User have no permission to access the project."
        #     self._logger.error(log_message)
        #     raise BadRequestError(error_message)

        # exlude project_id, node_id
        update_data = request.model_dump(exclude={"project_id", "node_id"}, exclude_none=True)
        # transformed_data = {f"nodes.$.{k}": v for k, v in update_data.items()}

        # idx, node = find_index_and_value(request.node_id, current_project.nodes, lambda x: x._id)
        # if idx is None:
        #     log_message = f"Node with id {request.node_id} not found in project {project_id}."
        #     error_message = f"Node not found."
        #     self._logger.error(log_message)
        #     raise BadRequestError(error_message)

        # current_project.nodes[idx] = node.model_copy(update=update_data)

        # process update <project>.nodes
        update_result = self._collection.update_one(
            {"_id": project_id, "nodes._id": request.node_id},
            {"$set": {"nodes.$": {"_id": request.node_id, **update_data}}},
        )

        # nếu client mà request update node mà y chang origninal node thì modified_count vẫn sẽ = 0 -> không check kiểu này dc
        # check if update successfully
        if update_result.matched_count == 0:
            log_message = f"Update failed. no node with _id {request.node_id} found in project {project_id}."
            error_message = f"Update failed. No node found."
            self._logger.error(log_message)
            return self.Response(success=False, error_message=error_message, updated_node=None)

        if update_result.modified_count == 0:
            log_message = f"Update failed. Nothing new in requested data to update."
            error_message = f"Update failed. Nothing new in requested data to update."
            self._logger.error(log_message)
            return self.Response(success=False, error_message=error_message, updated_node=None)

        updated_node_data: t.Any = self._collection.find_one(
            {"_id": project_id, "nodes._id": request.node_id}, {"nodes": {"$elemMatch": {"_id": request.node_id}}}
        )

        # check if updated_node_data có field "nodes" hay không, nó có phải array không?

        if updated_node_data is None:
            log_message = f"Update succeed, but failed in retrieve data."
            error_message = f"Update succeed, but failed in retrieve data."
            self._logger.error(log_message)
            return self.Response(success=True, error_message=error_message, updated_node=None)

        # process response
        updated_node = ShapeModel(**updated_node_data["nodes"][0])
        return self.Response(updated_node=updated_node)


UpdateNodeDep = t.Annotated[UpdateNode, Depends()]
