import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method

IRemoveUserFromOrganization = IBaseComponent[
    "RemoveUserFromOrganization.Request", "RemoveUserFromOrganization.Response | None"
]


# TODO: handle add relationship with transaction
# Assume two operations will be done successfully
class RemoveUserFromOrganization(IRemoveUserFromOrganization):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._user_collection = db.get_collection(CollectionName.USERS)
        self._organization_collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger

    class Request(p.BaseModel):
        organization_id: PyObjectUUID
        user_id: PyObjectUUID

    class Response(p.BaseModel):
        success: bool

    async def aexecute(self, request: "Request") -> "Response | None":
        self._logger.info(execute_service_method(self))
        organization_id = request.organization_id
        user_id = request.user_id

        update_user_result = self._user_collection.update_one(
            {"_id": user_id},
            {
                "$pull": {"joined_organizations": {"organization_id": organization_id}},
            },
        )
        if not update_user_result.modified_count:
            self._logger.error(f"Failed to update user {user_id}")
            return None

        update_organization_result = self._organization_collection.update_one(
            {"_id": organization_id},
            {
                "$pull": {"members": {"member_id": user_id}},
            },
        )
        if not update_organization_result.modified_count:
            self._logger.error(f"Failed to update organization {organization_id}")
            return None

        return self.Response(success=True)


RemoveUserFromOrganizationDep = t.Annotated[RemoveUserFromOrganization, Depends()]
