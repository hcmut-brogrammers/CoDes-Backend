import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import JoinedOrganization, JoinOrganizationMember, PyObjectUUID, UserRole
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...interfaces import IBaseComponent
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method

IAddUserToOrganization = IBaseComponent["AddUserToOrganization.Request", "AddUserToOrganization.Response | None"]


# TODO: handle add relationship with transaction
# Assume two operations will be done successfully
class AddUserToOrganization(IAddUserToOrganization):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._user_collection = db.get_collection(CollectionName.USERS)
        self._organization_collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger

    class Request(p.BaseModel):
        organization_id: PyObjectUUID
        user_id: PyObjectUUID
        role: UserRole

    class Response(p.BaseModel):
        joined_organization: JoinedOrganization
        join_organization_member: JoinOrganizationMember

    async def aexecute(self, request: "Request") -> "Response | None":
        self._logger.info(execute_service_method(self))
        now = get_utc_now()
        organization_id = request.organization_id
        user_id = request.user_id
        role = request.role

        joined_organization = JoinedOrganization(organization_id=organization_id, role=role, joined_at=now)
        update_user_result = self._user_collection.update_one(
            {"_id": user_id},
            {
                "$push": {"joined_organizations": joined_organization.model_dump()},
            },
        )
        if not update_user_result.modified_count:
            self._logger.error(f"Failed to update user {user_id}")
            return None

        join_organization_member = JoinOrganizationMember(
            member_id=user_id,
            member_role=role,
            joined_at=now,
        )
        update_organization_result = self._organization_collection.update_one(
            {"_id": organization_id},
            {
                "$push": {"members": join_organization_member.model_dump()},
            },
        )
        if not update_organization_result.modified_count:
            self._logger.error(f"Failed to update organization {organization_id}")
            return None

        return self.Response(joined_organization=joined_organization, join_organization_member=join_organization_member)


AddUserToOrganizationDep = t.Annotated[AddUserToOrganization, Depends()]
