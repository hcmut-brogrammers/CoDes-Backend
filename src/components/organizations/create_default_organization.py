import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.models import OrganizationModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import InternalServerError
from ...interfaces.base_component import IBaseComponent
from ...utils.logger import execute_service_method

ICreateDefaultOrganization = IBaseComponent["CreateDefaultOrganization.Request", "CreateDefaultOrganization.Response"]


class CreateDefaultOrganization(ICreateDefaultOrganization):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger

    class Request(p.BaseModel):
        owner_id: UUID
        owner_name: str

    class Response(p.BaseModel):
        created_organization: OrganizationModel

    def gen_default_organization_name(self, owner_name: str) -> str:
        return f"{owner_name[0].upper() + owner_name[1:]}'s Default Organization"

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        # check if the owner already has a default organization
        filter = {
            "owner_id": request.owner_id,
            "is_default": True,
        }
        is_user_has_default_organization = self._collection.find_one(filter)
        if is_user_has_default_organization:
            log_message = f"User with id {request.owner_id} already has a default organization."
            error_message = f"User already has a default organization."
            self._logger.error(log_message)
            raise InternalServerError(error_message)

        # process create organization
        default_name = self.gen_default_organization_name(request.owner_name)
        default_avatar_url = "https://i.etsystatic.com/45893541/r/il/545bc4/6453954482/il_570xN.6453954482_q062.jpg"

        organization = OrganizationModel(
            name=default_name,
            avatar_url=default_avatar_url,
            owner_id=request.owner_id,
            is_default=True,
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


CreateDefaultOrganizationDep = t.Annotated[CreateDefaultOrganization, Depends()]
