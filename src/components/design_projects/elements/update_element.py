import typing as t

import pydantic as p
from fastapi import Depends

from ....common.models import ElementModel, PyObjectUUID
from ....constants.mongo import CollectionName
from ....dependencies import LoggerDep, MongoDbDep, UserContextDep
from ....exceptions import BadRequestError
from ....interfaces import IBaseComponent
from ....utils.logger import execute_service_method
from .base_update_element import BaseUpdateElementDep

IUpdateElement = IBaseComponent["UpdateElement.Request", "UpdateElement.Response"]


class UpdateElement(IUpdateElement):
    def __init__(
        self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep, base_update_element: BaseUpdateElementDep
    ) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context
        self._base_update_element = base_update_element

    class HttpRequest(p.BaseModel):
        element: ElementModel

    class Request(HttpRequest, p.BaseModel):
        project_id: PyObjectUUID
        element_id: PyObjectUUID

    class Response(p.BaseModel):
        updated_element: ElementModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        element_id = request.element_id
        base_update_element_request = self._base_update_element.Request(
            element=request.element,
            organization_id=self._user_context.organization_id,
            project_id=request.project_id,
            element_id=element_id,
        )
        base_update_element_response = await self._base_update_element.aexecute(base_update_element_request)
        if not base_update_element_response:
            self._logger.error(f"Failed to update element with id {element_id}.")
            raise BadRequestError(f"Failed to update element with id {element_id}.")

        updated_element = base_update_element_response.updated_element
        return self.Response(updated_element=updated_element)


UpdateElementDep = t.Annotated[UpdateElement, Depends()]
