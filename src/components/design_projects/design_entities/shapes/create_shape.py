import typing as t

import pydantic as p
from fastapi import Depends

from .....common.auth import UserContextDep
from .....common.models import PyObjectUUID
from .....constants.mongo import CollectionName
from .....dependencies import LoggerDep, MongoDbDep
from .....interfaces import IBaseComponent
from .....utils.logger import execute_service_method
from .base_create_shape import BaseCreateShape, BaseCreateShapeDep

ICreateShape = IBaseComponent["CreateShape.Request", "CreateShape.Response"]


class CreateShape(ICreateShape):
    def __init__(
        self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep, base_create_shape: BaseCreateShapeDep
    ) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context
        self._base_create_shape = base_create_shape

    class HttpRequest(BaseCreateShape.HttpRequest, p.BaseModel):
        pass

    class Request(HttpRequest, p.BaseModel):
        design_project_id: PyObjectUUID

    class Response(BaseCreateShape.Response, p.BaseModel):
        pass

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        design_project_id = request.design_project_id
        organization_id = self._user_context.organization_id
        base_create_shape_request = BaseCreateShape.Request(
            organization_id=organization_id, design_project_id=design_project_id, shape=request.shape
        )
        base_create_shape_response = await self._base_create_shape.aexecute(base_create_shape_request)
        return self.Response(**base_create_shape_response.model_dump())


CreateShapeDep = t.Annotated[CreateShape, Depends()]
