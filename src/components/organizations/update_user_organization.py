import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import OrganizationModel, PyObjectHttpUrlStr, PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import BadRequestError, NotFoundError
from ...interfaces import IBaseComponent
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method

IUpdateUserOrganization = IBaseComponent["UpdateUserOrganization.Request", "UpdateUserOrganization.Response"]


class UpdateUserOrganization(IUpdateUserOrganization):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger
        self._user_context = user_context

    class HttpRequest(p.BaseModel):
        name: str | None = p.Field(default=None)
        avatar_url: PyObjectHttpUrlStr | None = p.Field(default=None)

    class Request(HttpRequest, p.BaseModel):
        organization_id: PyObjectUUID

    class Response(p.BaseModel):
        updated_organization: OrganizationModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        update_data = request.model_dump(exclude={"organization_id"}, exclude_none=True)
        if not update_data:
            error_message = f"No fields to update for organization id {request.organization_id}."
            self._logger.info(error_message)
            raise BadRequestError(error_message)

        # before update condition check
        filter = {
            "_id": request.organization_id,
            "owner_id": self._user_context.user_id,
        }
        organization_data = self._collection.find_one(filter)
        if organization_data is None:
            error_message = f"Organization with id {request.organization_id} not found."
            self._logger.error(error_message)
            raise NotFoundError(error_message)

        organization = OrganizationModel(**organization_data)
        updated_organization = organization.model_copy(update=update_data)
        updated_organization.updated_at = get_utc_now()
        self._collection.update_one(
            {"_id": updated_organization.id}, {"$set": updated_organization.model_dump(exclude={"id"})}
        )
        return self.Response(updated_organization=updated_organization)


UpdateUserOrganizationDep = t.Annotated[UpdateUserOrganization, Depends()]
