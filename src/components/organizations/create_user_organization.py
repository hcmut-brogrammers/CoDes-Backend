import typing as t

import pydantic as p
from fastapi import Depends
from pydantic import BaseModel

from ...common.models import OrganizationModel, PyObjectHttpUrlStr, UserRole
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method
from .create_organization import CreateOrganization, CreateOrganizationDep

ICreateUserOrganization = IBaseComponent["CreateUserOrganization.Request", "CreateUserOrganization.Response"]


class CreateUserOrganization(ICreateUserOrganization):
    def __init__(
        self,
        db: MongoDbDep,
        logger: LoggerDep,
        user_context: UserContextDep,
        create_organization: CreateOrganizationDep,
    ) -> None:
        self._collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger
        self._user_context = user_context
        self._create_organization = create_organization

    class Request(BaseModel):
        name: str = p.Field(default="Default Organization")
        avatar_url: PyObjectHttpUrlStr | None = p.Field(default=None)

    class Response(p.BaseModel):
        created_organization: OrganizationModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        # check if the owner already has a default organization
        filter = {
            "owner_id": self._user_context.user_id,
            "is_default": True,
        }
        organization_data = self._collection.find_one(filter)
        create_organization_request = CreateOrganization.Request(
            name=request.name,
            avatar_url=request.avatar_url,
            owner_id=self._user_context.user_id,
            is_default=True if not organization_data else False,
            role=UserRole.OrganizationAdmin,
        )
        create_organization_response = await self._create_organization.aexecute(create_organization_request)
        return self.Response(created_organization=create_organization_response.created_organization)


CreateUserOrganizationDep = t.Annotated[CreateUserOrganization, Depends()]
