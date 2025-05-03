import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from .....common.auth.user_context import UserContextDep
from .....common.design_entities.type import GlobalCompositeOperationType, Vector2d
from .....common.models import DesignProjectModel
from .....common.models.design_entities.node import NodeModel
from .....constants.mongo import CollectionName
from .....dependencies import LoggerDep, MongoDbDep
from .....exceptions import BadRequestError
from .....interfaces.base_component import IBaseComponent
from .....utils.logger import execute_service_method
from .abstract_create_node import AbstractCreateNode, AbstractCreateNodeDep

ICreateNode = IBaseComponent["CreateNode.Request", "CreateNode.Response"]


class CreateNode(ICreateNode):
    def __init__(
        self,
        db: MongoDbDep,
        logger: LoggerDep,
        user_context: UserContextDep,
        abstract_create_node: AbstractCreateNodeDep,
    ) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context
        self._abstract_create_node = abstract_create_node

    class BaseHttpRequest(AbstractCreateNode.BaseHttpRequest):
        pass

    class HttpRequest(AbstractCreateNode.HttpRequest, p.BaseModel):
        pass

    class Request(BaseHttpRequest, p.BaseModel):
        project_id: UUID

    class Response(AbstractCreateNode.Response, p.BaseModel):
        pass

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        organization_id = self._user_context.organization_id

        abstract_create_node_request = AbstractCreateNode.Request(
            **request.model_dump(),
            organization_id=organization_id,
            project_id=request.project_id,
        )
        abstract_create_node_response = await self._abstract_create_node.aexecute(abstract_create_node_request)
        # return await self._abstract_create_node.aexecute(abstract_create_node_request)
        return self.Response(**abstract_create_node_response.model_dump())
        # return t.cast(CreateNode.Response, await self._abstract_create_node.aexecute(abstract_create_node_request))


CreateNodeDep = t.Annotated[CreateNode, Depends()]
