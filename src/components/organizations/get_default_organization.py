import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.models import OrganizationModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import NotFoundError
from ...interfaces.base_component import IBaseComponent
from ...utils.logger import execute_service_method

IGetDefaultOrganization = IBaseComponent[
    "GetDefaultOrganization.Request",
    "GetDefaultOrganization.Response",
]


class GetDefaultOrganization(IGetDefaultOrganization):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger

    class Request(p.BaseModel):
        owner_id: UUID

    class Response(p.BaseModel):
        organization: OrganizationModel

    async def aexecute(self, request: Request) -> "Response":
        self._logger.info(execute_service_method(self))
        filter = {"owner_id": request.owner_id, "is_default": True}
        organizations_data = self._collection.find_one(filter)

        if not organizations_data:
            error_message = f"No default organization with owner_id {request.owner_id} is found."
            self._logger.error(error_message)
            raise NotFoundError(error_message)

        organization = OrganizationModel(**organizations_data)
        return self.Response(organization=organization)


GetDefaultOrganizationDep = t.Annotated[GetDefaultOrganization, Depends()]
