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

IUpdateOrganization = IBaseComponent["UpdateOrganization.Request", "UpdateOrganization.Response"]


class UpdateOrganization(IUpdateOrganization):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger
        self._user_context = user_context

    class HttpRequest(p.BaseModel):
        name: str | None = None
        avatar_url: p.HttpUrl | None = None

    class Request(HttpRequest, p.BaseModel):
        organization_id: UUID

    class Response(p.BaseModel):
        updated_organization: OrganizationModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        self._logger.info(self._user_context)

        # update proccess
        update_data = request.model_dump(exclude={"organization_id", "is_default"}, exclude_none=True)

        # cast: HttpUrl -> str
        update_data["avatar_url"] = str(request.avatar_url)

        if not update_data:
            self._logger.info(f"No fields to update for organization id {request.organization_id}")
            raise BadRequestError("No fields to update")

        # before update condition check
        filter = {
            "_id": request.organization_id,
            "owner_id": self._user_context.user_id,
            "is_deleted": False,
        }
        current_organization = self._collection.find_one(filter)

        # NOTE: redefine Error message
        if current_organization is None:
            self._logger.error(f"Organization with id {request.organization_id} not found")
            raise NotFoundError(f"Organization with id {request.organization_id} not found")

        updated_organization = OrganizationModel(**current_organization).model_copy(update=update_data)
        updated_organization.updated_at = get_utc_now()

        self._collection.update_one(
            {"_id": updated_organization.id}, {"$set": updated_organization.model_dump(exclude={"id"})}
        )
        return self.Response(updated_organization=updated_organization)


UpdateOrganizationDep = t.Annotated[UpdateOrganization, Depends()]
