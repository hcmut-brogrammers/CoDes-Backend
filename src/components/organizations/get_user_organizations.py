import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import OrganizationModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import NotFoundError
from ...interfaces.base_component import IBaseComponentWithoutRequest
from ...utils.logger import execute_service_method
from ..users import GetUserById, GetUserByIdDep

IGetUserOrganizations = IBaseComponentWithoutRequest["GetUserOrganizations.Response"]


class GetUserOrganizations(IGetUserOrganizations):
    def __init__(
        self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep, get_user_by_id: GetUserByIdDep
    ) -> None:
        self._collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger
        self._user_context = user_context
        self._get_user_by_id = get_user_by_id

    class Response(p.BaseModel):
        organizations: list[OrganizationModel]

    async def aexecute(self) -> "Response":
        self._logger.info(execute_service_method(self))
        get_user_by_id_response = await self._get_user_by_id.aexecute(
            GetUserById.Request(user_id=self._user_context.user_id)
        )
        user = get_user_by_id_response.user
        if not user:
            self._logger.error(f"User with id {self._user_context.user_id} is not found.")
            raise NotFoundError(f"User with id {self._user_context.user_id} is not found.")

        joined_organizations = user.joined_organizations
        joined_organization_ids = [item.organization_id for item in joined_organizations]
        filter = {"_id": {"$in": joined_organization_ids}}
        # filter = {"owner_id": self._user_context.user_id}
        organizations_data = self._collection.find(filter)
        if not organizations_data:
            self._logger.error(f"No organization that owner_id {self._user_context.user_id} joined is found.")
            raise NotFoundError(f"No organization that owner_id {self._user_context.user_id} joined is found.")

        organizations = [OrganizationModel(**organization) for organization in organizations_data]
        return self.Response(organizations=organizations)


GetUserOrganizationsDep = t.Annotated[GetUserOrganizations, Depends()]
