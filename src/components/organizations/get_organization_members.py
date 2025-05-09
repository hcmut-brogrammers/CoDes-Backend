import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import PyObjectDatetime, PyObjectUUID, UserModel, UserRole
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...interfaces import IBaseComponent
from ...utils.common import find
from ...utils.logger import execute_service_method
from ..users import GetUserByIdDep
from .get_organization_by_id import GetOrganizationById, GetOrganizationByIdDep

IGetOrganizationMembers = IBaseComponent["GetOrganizationMembers.Request", "GetOrganizationMembers.Response"]


class GetOrganizationMembers(IGetOrganizationMembers):
    def __init__(
        self,
        db: MongoDbDep,
        logger: LoggerDep,
        get_user_by_id: GetUserByIdDep,
        get_organization_by_id: GetOrganizationByIdDep,
    ) -> None:
        self._collection = db.get_collection(CollectionName.USERS)
        self._logger = logger
        self._get_user_by_id = get_user_by_id
        self._get_organization_by_id = get_organization_by_id

    class Member(p.BaseModel):
        member_id: PyObjectUUID
        username: str
        email: str
        role: UserRole
        joined_at: PyObjectDatetime

    class Request(p.BaseModel):
        organization_id: PyObjectUUID

    class Response(p.BaseModel):
        members: list["GetOrganizationMembers.Member"] = p.Field(default=[])

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        organization_id = request.organization_id
        get_organization_by_id_request = GetOrganizationById.Request(
            id=organization_id,
        )
        get_organization_by_id_response = await self._get_organization_by_id.aexecute(get_organization_by_id_request)
        organization = get_organization_by_id_response.organization
        if not organization:
            self._logger.error(f"Organization with id {organization_id} is not found.")
            return self.Response(members=[])

        member_ids = [member.member_id for member in organization.members]
        query = {"_id": {"$in": member_ids}}
        users_data = self._collection.find(query)
        if not users_data:
            self._logger.error(f"No members found for organization with id {organization_id}.")
            return self.Response(members=[])

        users = [UserModel(**user_data) for user_data in users_data]
        members: list["GetOrganizationMembers.Member"] = []
        for user in users:
            member = find(organization.members, lambda x: x.member_id == user.id)
            if not member:
                self._logger.error(f"Member with id {user.id} is not found in organization {organization_id}.")
                continue

            members.append(
                self.Member(
                    member_id=user.id,
                    username=user.username,
                    email=user.email,
                    role=member.member_role,
                    joined_at=member.joined_at,
                )
            )
        return self.Response(members=members)


GetOrganizationMembersDep = t.Annotated[GetOrganizationMembers, Depends()]
