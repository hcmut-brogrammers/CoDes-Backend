import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.models import OrganizationModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import NotFoundError
from ...interfaces.base_component import IBaseComponent
from ...utils.logger import execute_service_method

IGetOrganizationById = IBaseComponent["GetOrganizationById.Request", "GetOrganizationById.Response"]


class GetOrganizationById(IGetOrganizationById):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger

    class Request(p.BaseModel):
        id: UUID

    class Response(p.BaseModel):
        organization: OrganizationModel

    async def aexecute(self, request: Request) -> "Response":
        self._logger.info(execute_service_method(self))
        organization_id = request.id
        filter = {"_id": organization_id}
        organization_data = self._collection.find_one(filter)

        if not organization_data:
            log_message = f"No organization with id {organization_id} is found."
            error_message = f"No organization with is found."
            self._logger.error(log_message)
            raise NotFoundError(error_message)

        organization = OrganizationModel(**organization_data)
        return self.Response(organization=organization)


GetOrganizationByIdDep = t.Annotated[GetOrganizationById, Depends()]
