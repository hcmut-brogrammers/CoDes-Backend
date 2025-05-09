import typing as t

import pydantic as p
from fastapi import Depends

from ....common.auth import UserContextDep
from ....common.models import PyObjectUUID
from ....constants.mongo import CollectionName
from ....dependencies import LoggerDep, MongoDbDep
from ....interfaces import IBaseComponent
from ....utils.logger import execute_service_method
from .base_delete_element import BaseDeleteElement, BaseDeleteElementDep

IDeleteElement = IBaseComponent["DeleteElement.Request", "DeleteElement.Response"]


class DeleteElement(IDeleteElement):
    def __init__(
        self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep, base_delete_element: BaseDeleteElementDep
    ) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context
        self._base_delete_element = base_delete_element

    class Request(p.BaseModel):
        project_id: PyObjectUUID
        element_id: PyObjectUUID

    class Response(BaseDeleteElement.Response):
        pass

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        organization_id = self._user_context.organization_id
        project_id = request.project_id
        element_id = request.element_id
        base_delete_element_request = self._base_delete_element.Request(
            organization_id=organization_id, project_id=project_id, element_id=element_id
        )
        base_delete_element_response = await self._base_delete_element.aexecute(base_delete_element_request)
        if base_delete_element_response.success == False:
            self._logger.error(f"Failed to delete element with id {element_id} in project {project_id}.")
            return self.Response(success=False)

        return self.Response(success=True)


DeleteElementDep = t.Annotated[DeleteElement, Depends()]
