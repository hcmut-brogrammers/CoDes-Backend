from uuid import UUID

from fastapi import APIRouter, status

from ...components.authenticate import (
    Regen_access_token_for_switching_organization,
    Regen_access_token_for_switching_organizationDep,
)
from ...components.join_workspace_invitations import CreateMultiJoinOrganizationInvitationDep as CreateMultiInvitation
from ...constants.router import ApiPath

router = APIRouter(
    prefix=ApiPath.JOIN_WORKSPACE_INVITATIONS,
    tags=["join-workspace-invitations"],
)


@router.post(
    "",
    response_model=CreateMultiInvitation.Response,
    response_description="Join Organization Invitations created",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_multi_invitations(create_organization: CreateMultiInvitation, request: CreateMultiInvitation.Request):
    return await create_organization.aexecute(request)


@router.post(
    ApiPath.SWITCH_ORGANIZATION,
    response_model=Regen_access_token_for_switching_organizationDep.Response,
    response_description="re-generate access token for switching organizaiton successfully",
    response_model_by_alias=False,
    status_code=200,
)
async def regen_access_token_for_switching_organization(
    regen_access_token: Regen_access_token_for_switching_organizationDep,
    request: Regen_access_token_for_switching_organization.Request,
):
    return await regen_access_token.aexecute(request)
