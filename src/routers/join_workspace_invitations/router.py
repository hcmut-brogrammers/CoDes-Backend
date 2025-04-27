from fastapi import APIRouter, status

from ...components.join_organization_invitations import CreateBatchJoinOrganizationInvitationDep, GetUserInvitationsDep
from ...constants.router import ApiPath

router = APIRouter(
    prefix=ApiPath.JOIN_WORKSPACE_INVITATIONS,
    tags=["join-workspace-invitations"],
)


@router.post(
    "",
    response_model=CreateBatchJoinOrganizationInvitationDep.Response,
    response_description="Join Organization Invitations created",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_multi_invitations(
    create_organization: CreateBatchJoinOrganizationInvitationDep,
    request: CreateBatchJoinOrganizationInvitationDep.Request,
):
    return await create_organization.aexecute(request)


@router.get(
    "",
    response_model=GetUserInvitationsDep.Response,
    response_description="Join Organization Invitations created",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def get_invitations_for_receiver(create_organization: GetUserInvitationsDep):
    return await create_organization.aexecute()
