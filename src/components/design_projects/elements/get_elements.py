import typing as t

import pydantic as p
from fastapi import Depends

from ....common.models import PyObjectUUID
from ....constants.mongo import CollectionName
from ....dependencies import LoggerDep, MongoDbDep, UserContextDep
from ....interfaces import IBaseComponent
from ....utils.logger import execute_service_method
from .base_get_elements import BaseGetElements, BaseGetElementsDep

IGetElements = IBaseComponent["GetElements.Request", "GetElements.Response"]


class GetElements(IGetElements):
    def __init__(
        self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep, base_get_elements: BaseGetElementsDep
    ) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context
        self._base_get_elements = base_get_elements

    class Request(p.BaseModel):
        project_id: PyObjectUUID

    class Response(BaseGetElements.Response, p.BaseModel):
        pass

    async def aexecute(self, request: Request) -> "Response":
        self._logger.info(execute_service_method(self))

        project_id = request.project_id
        organization_id = self._user_context.organization_id
        base_get_elements_request = BaseGetElements.Request(organization_id=organization_id, project_id=project_id)
        base_get_elements_response = await self._base_get_elements.aexecute(base_get_elements_request)
        return self.Response(**base_get_elements_response.model_dump())


GetElementsDep = t.Annotated[GetElements, Depends()]
