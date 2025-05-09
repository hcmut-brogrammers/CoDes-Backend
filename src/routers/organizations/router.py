from fastapi import APIRouter, status

from ...common.models import PyObjectUUID
from ...components.organizations import (
    CreateUserOrganizationDep,
    DeleteOrganizationByIdDep,
    GetOrganizationById,
    GetOrganizationByIdDep,
    GetOrganizationMembers,
    GetOrganizationMembersDep,
    GetUserOrganizationMembers,
    GetUserOrganizationMembersDep,
    GetUserOrganizationsDep,
    LeaveOrganization,
    LeaveOrganizationDep,
    UninviteOrganzationMember,
    UninviteOrganzationMemberDep,
    UpdateUserOrganizationDep,
)
from ...components.switch_organization import SwitchOrganization, SwitchOrganizationDep
from ...constants.router import ApiPath

router = APIRouter(
    prefix=ApiPath.ORGANIZATIONS,
    tags=["organizations"],
)


@router.get(
    "",
    response_model=GetUserOrganizationsDep.Response,
    response_description="List of user organizations",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_organizations_by_owner_id(get_organizations_by_owner_id: GetUserOrganizationsDep):
    return await get_organizations_by_owner_id.aexecute()


@router.get(
    "/members",
    response_model=GetUserOrganizationMembers.Response,
    response_description="List of members in the current organization",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_user_organization_members(get_user_organization_members: GetUserOrganizationMembersDep):
    return await get_user_organization_members.aexecute()


@router.get(
    "/{organization_id}/members",
    response_model=GetOrganizationMembers.Response,
    response_description="List of members in the current organization",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_organization_members(get_organization_members: GetOrganizationMembersDep, organization_id: PyObjectUUID):
    return await get_organization_members.aexecute(GetOrganizationMembers.Request(organization_id=organization_id))


@router.get(
    "/{organization_id}",
    response_model=GetOrganizationByIdDep.Response,
    response_description="Organization found",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_organization_by_id(get_organization_by_id: GetOrganizationByIdDep, organization_id: PyObjectUUID):
    return await get_organization_by_id.aexecute(GetOrganizationById.Request(id=organization_id))


@router.post(
    "",
    response_model=CreateUserOrganizationDep.Response,
    response_description="Organization created",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(
    create_organization: CreateUserOrganizationDep, request: CreateUserOrganizationDep.Request
):
    return await create_organization.aexecute(request)


@router.post(
    "/leave",
    response_model=LeaveOrganization.Response,
    response_description="Leave organization",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def leave_organization(
    leave_organization: LeaveOrganizationDep,
):
    return await leave_organization.aexecute()


@router.post(
    "/uninvite-member",
    response_model=UninviteOrganzationMember.Response,
    response_description="Uninvite organization member",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def uninvite_organization_member(
    uninvite_organization_member: UninviteOrganzationMemberDep, request: UninviteOrganzationMember.Request
):
    return await uninvite_organization_member.aexecute(request)


@router.put(
    "/{organization_id}",
    response_model=UpdateUserOrganizationDep.Response,
    response_description="Organization updated",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def update_organization(
    update_organization: UpdateUserOrganizationDep,
    organization_id: PyObjectUUID,
    request: UpdateUserOrganizationDep.HttpRequest,
):
    return await update_organization.aexecute(
        UpdateUserOrganizationDep.Request(organization_id=organization_id, **request.model_dump())
    )


@router.delete(
    "/{organization_id}",
    response_model=DeleteOrganizationByIdDep.Response,
    response_description="Organization deleted",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def delete_organization_by_id(deleted_organization: DeleteOrganizationByIdDep, organization_id: PyObjectUUID):
    return await deleted_organization.aexecute(DeleteOrganizationByIdDep.Request(organization_id=organization_id))


@router.post(
    ApiPath.SWITCH_ORGANIZATION,
    response_model=SwitchOrganizationDep.Response,
    response_description="re-generate access token for switching organizaiton successfully",
    response_model_by_alias=False,
    status_code=200,
)
async def regen_access_token_for_switching_organization(
    regen_access_token: SwitchOrganizationDep,
    request: SwitchOrganization.Request,
):
    return await regen_access_token.aexecute(request)
