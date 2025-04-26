from uuid import UUID

from fastapi import APIRouter, status

from ...components.join_workspace_invitations import CreateMultiJoinOrganizationInvitationDep as CreateMultiInvitation
from ...components.join_workspace_invitations import GetInvitationsForReceiverDep, UpdateInvitationStatusForReceiverDep
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


@router.get(
    "",
    response_model=GetInvitationsForReceiverDep.Response,
    response_description="Get Organization Invitations For Receiver",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def get_invitations_for_receiver(create_organization: GetInvitationsForReceiverDep):
    return await create_organization.aexecute()


@router.put(
    "",
    response_model=UpdateInvitationStatusForReceiverDep.Response,
    response_description="Update Organization Invitations For Receiver",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def update_invitation_status_for_receiver(
    update_inivitation: UpdateInvitationStatusForReceiverDep, request: UpdateInvitationStatusForReceiverDep.Request
):
    return await update_inivitation.aexecute(request)
