import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.models import DesignProjectModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...interfaces.base_component import IBaseComponentWithoutRequest
from ...utils.logger import execute_service_method

IGetDesignProjectsByOrganizationId = IBaseComponentWithoutRequest["GetDesignProjectsByOrganizationId.Response"]


class GetDesignProjectsByOrganizationId(IGetDesignProjectsByOrganizationId):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context

    class Response(p.BaseModel):
        projects: t.List[DesignProjectModel]

    async def aexecute(self) -> "Response":
        self._logger.info(execute_service_method(self))
        filter = {"organization_id": self._user_context.organization_id}
        projects_data = self._collection.find(filter)

        projects = [DesignProjectModel(**project) for project in projects_data]
        return self.Response(projects=projects)


GetDesignProjectsByOrganizationIdDep = t.Annotated[GetDesignProjectsByOrganizationId, Depends()]
