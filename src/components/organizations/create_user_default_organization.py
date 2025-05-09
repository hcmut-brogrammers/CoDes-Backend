import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import OrganizationModel, PyObjectUUID, UserRole
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import BadRequestError
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method
from .create_organization import CreateOrganization, CreateOrganizationDep

ICreateUserDefaultOrganization = IBaseComponent[
    "CreateUserDefaultOrganization.Request", "CreateUserDefaultOrganization.Response"
]

DEFAULT_AVATAR_URL = "https://i.etsystatic.com/45893541/r/il/545bc4/6453954482/il_570xN.6453954482_q062.jpg"


class CreateUserDefaultOrganization(ICreateUserDefaultOrganization):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, create_organization: CreateOrganizationDep) -> None:
        self._collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger
        self._create_organization = create_organization

    class Request(p.BaseModel):
        owner_id: PyObjectUUID
        owner_username: str

    class Response(p.BaseModel):
        created_organization: OrganizationModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        owner_id = request.owner_id

        # check if the owner already has a default organization
        filter = {
            "owner_id": owner_id,
            "is_default": True,
        }
        organization_data = self._collection.find_one(filter)
        if organization_data:
            log_message = (
                f"the user {owner_id} has already owned a default organization. Can not create another default."
            )
            error_message = f"the user has already owned a default organization. Can not create another default."
            self._logger.error(log_message)
            raise BadRequestError(error_message)

        create_organization_request = CreateOrganization.Request(
            name=self._make_default_organization_name(request.owner_username),
            avatar_url=DEFAULT_AVATAR_URL,
            owner_id=owner_id,
            is_default=True,
            role=UserRole.OrganizationAdmin,
        )
        create_organization_response = await self._create_organization.aexecute(create_organization_request)
        return self.Response(created_organization=create_organization_response.created_organization)

    def _make_default_organization_name(self, username: str) -> str:
        return f"{username[0].upper() + username[1:]}'s Default Organization"


CreateUserDefaultOrganizationDep = t.Annotated[CreateUserDefaultOrganization, Depends()]
