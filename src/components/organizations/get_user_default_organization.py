import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import OrganizationModel, PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import NotFoundError
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method

IGetUserDefaultOrganization = IBaseComponent[
    "GetUserDefaultOrganization.Request",
    "GetUserDefaultOrganization.Response",
]


class GetUserDefaultOrganization(IGetUserDefaultOrganization):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger

    class Request(p.BaseModel):
        owner_id: PyObjectUUID

    class Response(p.BaseModel):
        organization: OrganizationModel

    async def aexecute(self, request: Request) -> "Response":
        self._logger.info(execute_service_method(self))
        filter = {"owner_id": request.owner_id, "is_default": True}
        organization_data = self._collection.find_one(filter)
        if not organization_data:
            self._logger.error(f"No default organization with owner_id {request.owner_id} is found.")
            raise NotFoundError(f"No default organization with owner_id {request.owner_id} is found.")

        organization = OrganizationModel(**organization_data)
        return self.Response(organization=organization)


GetUserDefaultOrganizationDep = t.Annotated[GetUserDefaultOrganization, Depends()]
