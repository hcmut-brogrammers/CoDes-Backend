import typing as t

import pydantic as p
from fastapi import Depends

from ....common.auth.user_context import UserContextDep
from ....common.models import BaseElementModel, PyObjectUUID
from ....constants.mongo import CollectionName
from ....dependencies import LoggerDep, MongoDbDep
from ....interfaces import IBaseComponent
from ....utils.logger import execute_service_method
from .base_create_element import BaseCreateElement, BaseCreateElementDep

ICreateElement = IBaseComponent["CreateElement.Request", "CreateElement.Response"]


class CreateElement(ICreateElement):
    def __init__(
        self,
        db: MongoDbDep,
        logger: LoggerDep,
        user_context: UserContextDep,
        base_create_element: BaseCreateElementDep,
    ) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context
        self._base_create_element = base_create_element

    class HttpRequest(p.BaseModel):
        element: BaseElementModel

    class Request(HttpRequest, p.BaseModel):
        design_project_id: PyObjectUUID

    class Response(BaseCreateElement.Response, p.BaseModel):
        pass

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        design_project_id = request.design_project_id
        organization_id = self._user_context.organization_id
        base_create_element_request = BaseCreateElement.Request(
            design_project_id=design_project_id, organization_id=organization_id, element=request.element
        )
        base_create_element_response = await self._base_create_element.aexecute(base_create_element_request)
        return self.Response(**base_create_element_response.model_dump())


CreateElementDep = t.Annotated[CreateElement, Depends()]
