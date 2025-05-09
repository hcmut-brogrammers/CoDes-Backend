import typing as t

import pydantic as p
from fastapi import Depends
from pymongo import UpdateOne

from .....common.auth import UserContextDep
from .....common.models import NodeModel, PyObjectUUID
from .....constants.mongo import CollectionName
from .....dependencies import LoggerDep, MongoDbDep
from .....exceptions import BadRequestError
from .....interfaces import IBaseComponent
from .....utils.logger import execute_service_method
from .create_node import CreateNode

ICreateBatchNodes = IBaseComponent["CreateBatchNodes.Request", "CreateBatchNodes.Response"]


class CreateBatchNodes(ICreateBatchNodes):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context

    class BaseHttpRequest:
        nodes: list[CreateNode.HttpRequest]

    class HttpRequest(BaseHttpRequest, p.BaseModel):
        pass

    class Request(BaseHttpRequest, p.BaseModel):
        project_id: PyObjectUUID

    class Response(p.BaseModel):
        success: bool = True
        error_message: str | None = None
        # updated_nodes: ShapeElementModel | None = None

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

        # # current_project.nodes.append(node)
        # current_project.nodes.insert(0, node)
        # self._collection.update_one(
        #     {"_id": project_id}, {"$set": current_project.model_dump(exclude={"id"}, exclude_none=True)}
        # )

        # create bulk operations
        bulk_operations = []
        for node in request.nodes:
            create_data = node.model_dump(by_alias=True, exclude_none=True)
            create_node = NodeModel(**create_data)
            bulk_operations.append(
                UpdateOne(
                    {"_id": project_id},
                    {
                        "$push": {
                            "nodes": {
                                "$each": [{**create_node.model_dump(by_alias=True, exclude_none=True)}],
                                "$position": 0,
                            }
                        }
                    },
                )
            )

        if not bulk_operations:
            return self.Response(success=False, error_message="No update operations provided.")

        # process bulk update operations
        try:
            result = self._collection.bulk_write(bulk_operations, ordered=False)
            # log bulk result data
            self._logger.info(result.bulk_api_result)
        except Exception as e:
            self._logger.error(f"Bulk update failed: {e}")
            return self.Response(success=False, error_message="Bulk update failed.")

        # process response
        return self.Response(success=True, error_message=None)


CreateBatchNodesDep = t.Annotated[CreateBatchNodes, Depends()]
