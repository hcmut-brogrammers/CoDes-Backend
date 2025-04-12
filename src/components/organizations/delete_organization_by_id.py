import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.models import OrganizationModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import BadRequestError, NotFoundError
from ...interfaces.base_component import IBaseComponent
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method

IDeleteOrganizationById = IBaseComponent["DeleteOrganizationById.Request", "DeleteOrganizationById.Response"]


class DeleteOrganizationById(IDeleteOrganizationById):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger
        self._user_context = user_context

    class Request(p.BaseModel):
        organization_id: UUID

    class Response(p.BaseModel):
        deleted_organization: OrganizationModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        # before delete condition check
        organization_id = request.organization_id

        filter = {
            "_id": organization_id,
            "owner_id": self._user_context.user_id,
            "is_deleted": False,
        }
        organization_data = self._collection.find_one(filter)

        if organization_data is None:
            error_message = f"Organization with id {organization_id} not found."
            self._logger.error(error_message)
            raise NotFoundError(error_message)

        organization = OrganizationModel(**organization_data)

        if organization.is_default is True:
            error_message = (
                f"Organization with id {organization_id} is a default one. The default organization cannot be deleted."
            )
            self._logger.error(error_message)
            raise BadRequestError(error_message)

        organization.is_deleted = True
        organization.deleted_at = get_utc_now()

        self._collection.update_one(
            {"_id": organization.id}, {"$set": organization.model_dump(exclude={"id", "is_default"})}
        )
        return self.Response(deleted_organization=organization)


DeleteOrganizationByIdDep = t.Annotated[DeleteOrganizationById, Depends()]
