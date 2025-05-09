import typing as t

import pydantic as p
from fastapi import Depends

from ....common.models import BaseElementModel, PyObjectUUID
from ....constants.mongo import CollectionName
from ....dependencies import LoggerDep, MongoDbDep, UserContextDep
from ....interfaces import IBaseComponent
from ....utils.logger import execute_service_method
from .base_create_batch_elements import BaseCreateBatchElements, BaseCreateBatchElementsDep

ICreateBatchElements = IBaseComponent["CreateBatchElements.Request", "CreateBatchElements.Response"]


class CreateBatchElements(ICreateBatchElements):
    def __init__(
        self,
        db: MongoDbDep,
        logger: LoggerDep,
        base_create_batch_elements: BaseCreateBatchElementsDep,
        user_context: UserContextDep,
    ) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._base_create_batch_elements = base_create_batch_elements
        self._user_context = user_context

    class HttpRequest(p.BaseModel):
        elements: list[BaseElementModel]

    class Request(HttpRequest, p.BaseModel):
        project_id: PyObjectUUID

    class Response(BaseCreateBatchElements.Response):
        pass

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        project_id = request.project_id
        organization_id = self._user_context.organization_id
        base_create_batch_elements_request = self._base_create_batch_elements.Request(
            base_elements=request.elements,
            organization_id=organization_id,
            project_id=project_id,
        )
        base_create_batch_elements_response = await self._base_create_batch_elements.aexecute(
            base_create_batch_elements_request
        )
        return self.Response(**base_create_batch_elements_response.model_dump())


CreateBatchElementsDep = t.Annotated[CreateBatchElements, Depends()]
