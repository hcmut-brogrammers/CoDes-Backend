from datetime import timedelta
from unittest.mock import AsyncMock, Mock, call
from uuid import UUID

import pytest

from ....common.models.join_organization_invitation import JoinOrganizationInvitationModel, Status
from ....components.join_workspace_invitations.create_join_organization_invitation import (
    INVITATION_EXPIRATION_DAYS,
    CreateJoinOrganizationInvitation,
)
from ....exceptions import InternalServerError
from ....utils.common import get_utc_now

MockSetUp = tuple[Mock, Mock, Mock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_user_context = Mock()
    mock_collection = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_user_context, mock_collection


class TestCreateOrganization:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_collection = mock_setup

        # Mock request and database response
        mock_organization_id = UUID("a3f5d9e2-8c67-4a01-9e45-2b70d4b4d1f3")
        mock_sender_id = UUID("e1c8b5a6-2d9f-4fb0-86f1-3c9c5ed4a8bb")
        mock_receiver_id = UUID("6b7fa9c2-3c7e-44a2-91c0-6c8e78db9e2a")

        # Mock user_context
        mock_user_context.configure_mock(
            user_id=mock_sender_id,
            organization_id=mock_organization_id,
        )

        mock_taken_at = get_utc_now()
        invitation = JoinOrganizationInvitationModel(
            organization_id=mock_organization_id,
            sender_id=mock_sender_id,
            receiver_id=mock_receiver_id,
            status=Status.pending,
            taken_action=None,
            taken_at=mock_taken_at,
            expires_at=mock_taken_at + timedelta(INVITATION_EXPIRATION_DAYS),
        )

        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=invitation.id)),
            find_one=Mock(return_value=invitation.model_dump(by_alias=True)),
        )

        # Initialize the component
        create_invitation = CreateJoinOrganizationInvitation(
            db=mock_db, logger=mock_logger, user_context=mock_user_context
        )

        # Execute the component
        request = CreateJoinOrganizationInvitation.Request(user_id=mock_receiver_id)
        response = await create_invitation.aexecute(request)

        # Assertions
        assert response.invitation is not None
        assert response.invitation.organization_id == mock_organization_id
        assert response.invitation.sender_id == mock_sender_id
        assert response.invitation.receiver_id == mock_receiver_id
        assert response.invitation.status == Status.pending
        assert response.invitation.taken_action is None

        # Verify interactions
        mock_collection.insert_one.assert_called_once()
        mock_collection.find_one.call_count == 1
        expect_calls = [call({"_id": invitation.id})]
        assert mock_collection.find_one.call_args_list == expect_calls

    @pytest.mark.asyncio
    async def test_aexecute_no_created_invitation_found_throw_exception(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_collection = mock_setup

        # Mock request and database response
        mock_organization_id = UUID("a3f5d9e2-8c67-4a01-9e45-2b70d4b4d1f3")
        mock_sender_id = UUID("e1c8b5a6-2d9f-4fb0-86f1-3c9c5ed4a8bb")
        mock_receiver_id = UUID("6b7fa9c2-3c7e-44a2-91c0-6c8e78db9e2a")

        # Mock user_context
        mock_user_context.configure_mock(
            user_id=mock_sender_id,
            organization_id=mock_organization_id,
        )

        mock_taken_at = get_utc_now()
        invitation = JoinOrganizationInvitationModel(
            organization_id=mock_organization_id,
            sender_id=mock_sender_id,
            receiver_id=mock_receiver_id,
            status=Status.pending,
            taken_action=None,
            taken_at=mock_taken_at,
            expires_at=mock_taken_at + timedelta(INVITATION_EXPIRATION_DAYS),
        )

        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=invitation.id)),
            find_one=Mock(return_value=None),
        )

        # Initialize the component
        create_invitation = CreateJoinOrganizationInvitation(
            db=mock_db, logger=mock_logger, user_context=mock_user_context
        )

        # Execute the component
        request = CreateJoinOrganizationInvitation.Request(user_id=mock_receiver_id)

        with pytest.raises(InternalServerError):
            await create_invitation.aexecute(request)

        # Verify interactions
        mock_collection.insert_one.assert_called_once()
        mock_collection.find_one.call_count == 1
        expect_calls = [call({"_id": invitation.id})]
        assert mock_collection.find_one.call_args_list == expect_calls
