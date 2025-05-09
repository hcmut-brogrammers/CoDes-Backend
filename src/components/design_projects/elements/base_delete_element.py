import typing as t

import pydantic as p
from fastapi import Depends

from ....common.models import PyObjectUUID
from ....constants.mongo import CollectionName
from ....dependencies import LoggerDep, MongoDbDep
from ....interfaces import IBaseComponent
from ....utils.logger import execute_service_method

IBaseDeleteElement = IBaseComponent["BaseDeleteElement.Request", "BaseDeleteElement.Response"]


class BaseDeleteElement(IBaseDeleteElement):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger

    class Request(p.BaseModel):
        organization_id: PyObjectUUID
        project_id: PyObjectUUID
        element_id: PyObjectUUID

    class Response(p.BaseModel):
        success: bool

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        project_id = request.project_id
        organization_id = request.organization_id
        element_id = request.element_id
        is_project_exist = self._collection.count_documents(
            {"_id": project_id, "organization_id": organization_id}, limit=1
        )
        if is_project_exist < 1:
            self._logger.error(f"Project with id {project_id} not found.")
            return self.Response(success=False)

        # NOTE: hard delete element
        update_one_result = self._collection.update_one(
            {"_id": project_id}, {"$pull": {"elements": {"_id": element_id}}}
        )
        if update_one_result.matched_count == 0:
            self._logger.error(f"Element with id {element_id} not found in project {project_id}.")
            return self.Response(success=False)

        if update_one_result.modified_count == 0:
            self._logger.error(f"Failed to modify element with id {element_id} in project {project_id}.")
            return self.Response(success=False)

        return self.Response(success=True)


BaseDeleteElementDep = t.Annotated[BaseDeleteElement, Depends()]
