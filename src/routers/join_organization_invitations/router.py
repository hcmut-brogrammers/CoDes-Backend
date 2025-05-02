from fastapi import APIRouter, status

from ...common.models import PyObjectUUID
from ...components.join_organization_invitations import (
    CreateBatchJoinOrganizationInvitationDep,
    GetUserInvitationsDep,
    MarkInvitationReadOrUnread,
    MarkInvitationReadOrUnreadDep,
)
from ...constants.router import ApiPath

router = APIRouter(
    prefix=ApiPath.JOIN_ORGANIZATION_INVITATIONS,
    tags=["join-organization-invitations"],
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


@router.post(
    "/{invitation_id}/mark-read",
    response_model=MarkInvitationReadOrUnread.Response,
    response_description="Invitations marked as read",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def mark_invitation_read(
    mark_invitation_read_or_unread: MarkInvitationReadOrUnreadDep,
    invitation_id: PyObjectUUID,
):
    return await mark_invitation_read_or_unread.aexecute(
        MarkInvitationReadOrUnread.Request(invitation_id=invitation_id, is_read=True)
    )


@router.post(
    "/{invitation_id}/mark-unread",
    response_model=MarkInvitationReadOrUnread.Response,
    response_description="Invitations marked as unread",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def mark_invitation_unread(
    mark_invitation_read_or_unread: MarkInvitationReadOrUnreadDep,
    invitation_id: PyObjectUUID,
):
    return await mark_invitation_read_or_unread.aexecute(
        MarkInvitationReadOrUnread.Request(invitation_id=invitation_id, is_read=False)
    )


@router.get(
    "",
    response_model=GetUserInvitationsDep.Response,
    response_description="Join Organization Invitations created",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def get_invitations_for_receiver(create_organization: GetUserInvitationsDep):
    return await create_organization.aexecute()
