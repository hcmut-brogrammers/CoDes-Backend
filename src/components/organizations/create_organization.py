import typing as t

import pydantic as p
from fastapi import Depends
from pydantic import BaseModel

from ...common.models import OrganizationModel, PyObjectHttpUrlStr, PyObjectUUID, UserRole
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import InternalServerError
from ...interfaces.base_component import IBaseComponent
from ...utils.logger import execute_service_method
from ..users import AddUserToOrganization, AddUserToOrganizationDep

ICreateOrganization = IBaseComponent["CreateOrganization.Request", "CreateOrganization.Response"]


class CreateOrganization(ICreateOrganization):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, add_user_to_organization: AddUserToOrganizationDep) -> None:
        self._collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger
        self._add_user_to_organization = add_user_to_organization

    class Request(BaseModel):
        name: str
        avatar_url: PyObjectHttpUrlStr | None = p.Field(default=None)
        owner_id: PyObjectUUID
        is_default: bool
        role: UserRole

    class Response(p.BaseModel):
        created_organization: OrganizationModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        owner_id = request.owner_id
        organization = OrganizationModel(
            name=request.name,
            avatar_url=request.avatar_url,
            owner_id=owner_id,
            is_default=request.is_default,
        )
        inserted_organization = self._collection.insert_one(organization.model_dump(by_alias=True))
        created_organization = self._collection.find_one({"_id": inserted_organization.inserted_id})
        if not created_organization:
            self._logger.error(
                f"Insert organization data with id {inserted_organization.inserted_id} successfully, but unable to find the created organization"
            )
            raise InternalServerError(
                "Insert organization data successfully, but unable to find the created organization"
            )

        add_user_to_organization_request = AddUserToOrganization.Request(
            organization_id=organization.id,
            user_id=owner_id,
            role=request.role,
        )
        add_user_to_organization_response = await self._add_user_to_organization.aexecute(
            add_user_to_organization_request
        )
        if not add_user_to_organization_response:
            self._logger.error(
                f"Insert organization data successfully, but unable to add user {owner_id} to the created organization"
            )
            raise InternalServerError(
                "Insert organization data successfully, but unable to add user to the created organization"
            )

        organization.members.append(add_user_to_organization_response.join_organization_member)
        return self.Response(created_organization=organization)


CreateOrganizationDep = t.Annotated[CreateOrganization, Depends()]
