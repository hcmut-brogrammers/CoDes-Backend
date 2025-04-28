import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.models import OrganizationModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import NotFoundError
from ...interfaces.base_component import IBaseComponentWithoutRequest
from ...utils.logger import execute_service_method

IGetOrganizationsByOwnerId = IBaseComponentWithoutRequest["GetOrganizationsByOwnerId.Response"]


class GetOrganizationsByOwnerId(IGetOrganizationsByOwnerId):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger
        self._user_context = user_context

    class Response(p.BaseModel):
        organizations: t.List["OrganizationModel"]

    async def aexecute(self) -> "Response":
        self._logger.info(execute_service_method(self))
        filter = {"owner_id": self._user_context.user_id}
        organizations_data = self._collection.find(filter)

        if not organizations_data:
            error_message = f"No organization with owner_id {self._user_context.user_id} is found."
            self._logger.error(error_message)
            raise NotFoundError(error_message)

        organizations = [OrganizationModel(**organization) for organization in organizations_data]
        return self.Response(organizations=organizations)


GetOrganizationByOwnerIdDep = t.Annotated[GetOrganizationsByOwnerId, Depends()]
