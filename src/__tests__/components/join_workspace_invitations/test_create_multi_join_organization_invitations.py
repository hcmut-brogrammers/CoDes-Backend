from datetime import timedelta
from unittest.mock import AsyncMock, Mock, call
from uuid import UUID, uuid4

import pytest

from ....common.models.join_organization_invitation import JoinOrganizationInvitationModel, Status
from ....common.models.organization import OrganizationModel
from ....components.join_workspace_invitations.create_join_organization_invitation import (
    INVITATION_EXPIRATION_DAYS,
    CreateJoinOrganizationInvitation,
)
from ....components.join_workspace_invitations.create_multi_join_organization_invitations import (
    CreateMultiJoinOrganizationInvitation,
)
from ....exceptions import BadRequestError, InternalServerError
from ....utils.common import get_utc_now

MockSetUp = tuple[Mock, Mock, Mock, AsyncMock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_user_context = Mock()
    mock_create_invitation = AsyncMock()
    mock_organization_collection = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_organization_collection))
    return mock_db, mock_logger, mock_user_context, mock_create_invitation, mock_organization_collection


class TestCreateOrganization:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_create_invitation, mock_organization_collection = mock_setup

        # Mock request and database response
        mock_organization_id = UUID("a3f5d9e2-8c67-4a01-9e45-2b70d4b4d1f3")
        mock_sender_id = UUID("e1c8b5a6-2d9f-4fb0-86f1-3c9c5ed4a8bb")
        mock_receivers_id = [
            UUID("6b7fa9c2-3c7e-44a2-91c0-6c8e78db9e2a"),
            UUID("0f1c61f0-e38e-11ee-89d1-0242ac120002"),
        ]

        # Mock user_context
        mock_user_context.configure_mock(
            user_id=mock_sender_id,
            organization_id=mock_organization_id,
        )

        mock_taken_at = get_utc_now()
        mock_invitations = [
            JoinOrganizationInvitationModel(
                organization_id=mock_organization_id,
                sender_id=mock_sender_id,
                receiver_id=mock_receiver_id,
                status=Status.pending,
                taken_action=None,
                taken_at=mock_taken_at,
                expires_at=mock_taken_at + timedelta(INVITATION_EXPIRATION_DAYS),
            )
            for mock_receiver_id in mock_receivers_id
        ]

        mock_organization = OrganizationModel(
            name="org_test",
            avatar_url="http://example.com/avatar.png",
            owner_id=mock_sender_id,
        )

        mock_organization_collection.configure_mock(
            find_one=Mock(return_value=mock_organization.model_dump(by_alias=True)),
        )

        response_create_invitation = [
            CreateJoinOrganizationInvitation.Response(invitation=mock_invitation)
            for mock_invitation in mock_invitations
        ]
        mock_create_invitation.configure_mock(aexecute=AsyncMock(side_effect=response_create_invitation))

        # Initialize the component
        create_multi_invitations = CreateMultiJoinOrganizationInvitation(
            db=mock_db,
            logger=mock_logger,
            user_context=mock_user_context,
            create_invitation=mock_create_invitation,
        )

        # Execute the component
        request = CreateMultiJoinOrganizationInvitation.Request(user_ids=mock_receivers_id)
        response = await create_multi_invitations.aexecute(request)

        # Assertions
        assert response.invitations is not None
        assert response.invitations is not []
        assert len(response.invitations) == len(mock_invitations)
        for invitation, mock_invitation in zip(response.invitations, mock_invitations):
            assert invitation.organization_id == mock_organization_id
            assert invitation.sender_id == mock_sender_id
            assert invitation.receiver_id == mock_invitation.receiver_id
            assert invitation.status == Status.pending
            assert invitation.taken_action is None

        # Verify interactions
        mock_organization_collection.find_one.call_count == 1
        filter = {
            "_id": mock_organization_id,
            "owner_id": mock_sender_id,
        }
        expect_calls = [call(filter)]
        assert mock_organization_collection.find_one.call_args_list == expect_calls

        mock_create_invitation.aexecute.call_count == len(mock_invitations)
        filter = {
            "_id": mock_organization_id,
            "owner_id": mock_sender_id,
        }
        expect_calls = [
            call(CreateJoinOrganizationInvitation.Request(user_id=mock_receiver_id))
            for mock_receiver_id in mock_receivers_id
        ]
        assert mock_create_invitation.aexecute.call_args_list == expect_calls

    @pytest.mark.asyncio
    async def test_aexecute_sender_not_own_the_organizaition(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_create_invitation, mock_organization_collection = mock_setup

        # Mock request and database response
        mock_organization_id = UUID("a3f5d9e2-8c67-4a01-9e45-2b70d4b4d1f3")
        mock_sender_id = UUID("e1c8b5a6-2d9f-4fb0-86f1-3c9c5ed4a8bb")
        mock_receivers_id = [
            UUID("6b7fa9c2-3c7e-44a2-91c0-6c8e78db9e2a"),
            UUID("0f1c61f0-e38e-11ee-89d1-0242ac120002"),
        ]

        # Mock user_context
        mock_user_context.configure_mock(
            user_id=mock_sender_id,
            organization_id=mock_organization_id,
        )

        mock_organization_collection.configure_mock(
            find_one=Mock(return_value=None),
        )

        # Initialize the component
        create_multi_invitations = CreateMultiJoinOrganizationInvitation(
            db=mock_db,
            logger=mock_logger,
            user_context=mock_user_context,
            create_invitation=mock_create_invitation,
        )

        # Execute the component
        request = CreateMultiJoinOrganizationInvitation.Request(user_ids=mock_receivers_id)
        with pytest.raises(BadRequestError):
            await create_multi_invitations.aexecute(request)

        # Verify interactions
        mock_organization_collection.find_one.call_count == 1
        filter = {
            "_id": mock_organization_id,
            "owner_id": mock_sender_id,
        }
        expect_calls = [call(filter)]
        assert mock_organization_collection.find_one.call_args_list == expect_calls
