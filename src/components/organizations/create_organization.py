import typing as t

import pydantic as p
from fastapi import Depends

from src.common.models.base import PyObjectUUID

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
        avatar_url: str | None = None

    class Response(p.BaseModel):
        created_organization: OrganizationModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        self._logger.info(self._user_context)

        organization = OrganizationModel(
            name=request.name,
            avatar_url=request.avatar_url,
            owner_id=self._user_context.user_id,
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
