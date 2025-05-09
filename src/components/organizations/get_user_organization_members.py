import typing as t

from fastapi import Depends

from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...interfaces import IBaseComponentWithoutRequest
from ...utils.logger import execute_service_method
from .get_organization_members import GetOrganizationMembers, GetOrganizationMembersDep

IGetUserOrganizationMembers = IBaseComponentWithoutRequest["GetUserOrganizationMembers.Response"]


class GetUserOrganizationMembers(IGetUserOrganizationMembers):
    def __init__(
        self,
        db: MongoDbDep,
        logger: LoggerDep,
        user_context: UserContextDep,
        get_organization_members: GetOrganizationMembersDep,
    ) -> None:
        self._user_collection = db.get_collection(CollectionName.USERS)
        self._logger = logger
        self._user_context = user_context
        self._get_organization_members = get_organization_members

    class Response(GetOrganizationMembers.Response):
        pass

    async def aexecute(self) -> "Response":
        self._logger.info(execute_service_method(self))
        organization_id = self._user_context.organization_id
        get_organization_members_request = GetOrganizationMembers.Request(
            organization_id=organization_id,
        )
        return self.Response(
            members=(await self._get_organization_members.aexecute(get_organization_members_request)).members
        )


GetUserOrganizationMembersDep = t.Annotated[GetUserOrganizationMembers, Depends()]
