import typing as t

import pydantic as p
from fastapi import Depends
from pymongo.cursor import Cursor

from ...common.models import OrganizationModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import InternalServerError
from ...interfaces.base_component import IBaseComponent
from ...utils.logger import execute_service_method

ICreateOrganization = IBaseComponent["CreateOrganization.Request", "CreateOrganization.Response"]


class CreateOrganization(ICreateOrganization):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger
        self._user_context = user_context

    class Request(p.BaseModel):
        name: str
        avatar_url: p.HttpUrl | None = None

    class Response(p.BaseModel):
        created_organization: OrganizationModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        self._logger.info(self._user_context)

        # check if the owner already has a default organization
        filter = {
            "is_deleted": False,
            "owner_id": self._user_context.user_id,
            "is_default": True,
        }
        data = self._collection.find_one(filter)

        # process create organization
        organization = OrganizationModel(
            name=request.name,
            avatar_url=str(request.avatar_url),  # cast HttpUrl -> str
            owner_id=self._user_context.user_id,
            is_default=True if not data else False,
        )
        organization_data = organization.model_dump(by_alias=True)
        inserted_organization = self._collection.insert_one(organization_data)
        created_organization = self._collection.find_one({"_id": inserted_organization.inserted_id})
        if not created_organization:
            self._logger.error(
                f"Insert organization data with id {inserted_organization.inserted_id} successfully, but unable to find the created organization"
            )
            raise InternalServerError(
                "Insert organization data successfully, but unable to find the created organization"
            )

        created_organization = OrganizationModel(**created_organization)
        return self.Response(created_organization=created_organization)


CreateOrganizationDep = t.Annotated[CreateOrganization, Depends()]
