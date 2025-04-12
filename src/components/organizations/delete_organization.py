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

    class HttpRequest(p.BaseModel):
        name: str | None = None
        avatar_url: str | None = None

    class Request(HttpRequest, p.BaseModel):
        organization_id: UUID

    class Response(p.BaseModel):
        deleted_organization: OrganizationModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        self._logger.info(self._user_context)

        # before delete condition check
        filter = {
            "_id": request.organization_id,
            "owner_id": self._user_context.user_id,
            "is_deleted": False,
        }
        current_organization = self._collection.find_one(filter)

        if current_organization is None:
            self._logger.error(f"Organization with id {request.organization_id} not found")
            raise NotFoundError(f"Organization with id {request.organization_id} not found")

        elif current_organization["is_default"] is True:
            self._logger.error(f"Organization with id {request.organization_id} is a default one")
            raise BadRequestError(f"Organization with id {request.organization_id} is a default one")

        deleted_time = get_utc_now()
        delete_data = {"is_deleted": True, "deleted_at": deleted_time}

        deleted_organization = OrganizationModel(**current_organization).model_copy(update=delete_data)

        self._collection.update_one(
            {"_id": deleted_organization.id}, {"$set": deleted_organization.model_dump(exclude={"id", "is_default"})}
        )
        return self.Response(deleted_organization=deleted_organization)


DeleteOrganizationByIdDep = t.Annotated[DeleteOrganizationById, Depends()]
