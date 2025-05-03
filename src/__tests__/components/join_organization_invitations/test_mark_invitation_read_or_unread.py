from unittest.mock import AsyncMock, Mock

import pydantic as p
import pytest
from pymongo.results import UpdateResult

from ....common.models import JoinOrganizationInvitationModel, Status
from ....components.join_organization_invitations.mark_invitation_read_or_unread import MarkInvitationReadOrUnread
from ....utils.common import generate_uuid, get_utc_now

MockSetUp = tuple[Mock, Mock, Mock, Mock, Mock, Mock]


class MockUpdateResult(p.BaseModel):
    modified_count: int


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_get_organization_by_id = Mock()
    mock_get_user_by_id = Mock()
    mock_db = Mock()
    mock_logger = Mock()
    mock_user_context = Mock()

    mock_collection = Mock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return (mock_get_organization_by_id, mock_get_user_by_id, mock_db, mock_logger, mock_user_context, mock_collection)


class TestMarkInvitationReadOrUnread:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_setup: MockSetUp) -> None:
        # Arrange
        (mock_get_organization_by_id, mock_get_user_by_id, mock_db, mock_logger, mock_user_context, mock_collection) = (
            mock_setup
        )

        mock_user_id = generate_uuid()
        mock_user_context.configure_mock(user_id=mock_user_id)
        mock_invitation_id = generate_uuid()
        mock_invitation = JoinOrganizationInvitationModel(
            _id=mock_invitation_id,
            organization_id=generate_uuid(),
            sender_id=generate_uuid(),
            receiver_id=mock_user_id,
            status=Status.Pending,
            expires_at=get_utc_now(),
            is_read=False,
        )
        mock_invitation_data = mock_invitation.model_dump(by_alias=True)

        mock_collection.configure_mock(find_one=Mock(return_value=mock_invitation_data))
        mock_update_one_result = MockUpdateResult(modified_count=1)
        mock_collection.configure_mock(update_one=Mock(return_value=mock_update_one_result))

        mock_collection.update_one.return_value.modified_count = 1

        mark_invitation_read_or_unread = MarkInvitationReadOrUnread(
            get_organization_by_id=mock_get_organization_by_id,
            get_user_by_id=mock_get_user_by_id,
            db=mock_db,
            logger=mock_logger,
            user_context=mock_user_context,
        )

        request = MarkInvitationReadOrUnread.Request(invitation_id=mock_invitation_id, is_read=True)

        # Act
        response = await mark_invitation_read_or_unread.aexecute(request)

        # Assert
        assert response.success is True
        mock_collection.find_one.assert_called_once_with({"_id": mock_invitation_id})
        mock_collection.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_invitation_not_found(self, mock_setup: MockSetUp) -> None:
        # Arrange
        (mock_get_organization_by_id, mock_get_user_by_id, mock_db, mock_logger, mock_user_context, mock_collection) = (
            mock_setup
        )

        mock_user_context.configure_mock(user_id=generate_uuid())
        mock_invitation_id = generate_uuid()

        mock_collection.configure_mock(find_one=Mock(return_value=None))

        mark_invitation_read_or_unread = MarkInvitationReadOrUnread(
            get_organization_by_id=mock_get_organization_by_id,
            get_user_by_id=mock_get_user_by_id,
            db=mock_db,
            logger=mock_logger,
            user_context=mock_user_context,
        )

        request = MarkInvitationReadOrUnread.Request(invitation_id=mock_invitation_id, is_read=True)

        # Act
        response = await mark_invitation_read_or_unread.aexecute(request)

        # Assert
        assert response.success is False
        mock_logger.error.assert_called_once_with(f"Invitation with id {mock_invitation_id} not found.")
        mock_collection.find_one.assert_called_once_with({"_id": mock_invitation_id})
        mock_collection.update_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_aexecute_invitation_not_belong_to_user(self, mock_setup: MockSetUp) -> None:
        # Arrange
        (mock_get_organization_by_id, mock_get_user_by_id, mock_db, mock_logger, mock_user_context, mock_collection) = (
            mock_setup
        )

        mock_user_id = generate_uuid()
        mock_user_context.configure_mock(user_id=mock_user_id)
        mock_invitation_id = generate_uuid()

        mock_invitation = JoinOrganizationInvitationModel(
            _id=mock_invitation_id,
            organization_id=generate_uuid(),
            sender_id=generate_uuid(),
            receiver_id=generate_uuid(),
            status=Status.Pending,
            expires_at=get_utc_now(),
            is_read=False,
        )
        mock_invitation_data = mock_invitation.model_dump(by_alias=True)

        mock_collection.configure_mock(find_one=Mock(return_value=mock_invitation_data))

        mark_invitation_read_or_unread = MarkInvitationReadOrUnread(
            get_organization_by_id=mock_get_organization_by_id,
            get_user_by_id=mock_get_user_by_id,
            db=mock_db,
            logger=mock_logger,
            user_context=mock_user_context,
        )

        request = MarkInvitationReadOrUnread.Request(invitation_id=mock_invitation_id, is_read=True)

        # Act
        response = await mark_invitation_read_or_unread.aexecute(request)

        # Assert
        assert response.success is False
        mock_logger.error.assert_called_once_with(
            f"Invitation with id {mock_invitation_id} does not belong to user {mock_user_id}."
        )
        mock_collection.find_one.assert_called_once_with({"_id": mock_invitation_id})
        mock_collection.update_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_aexecute_update_failed(self, mock_setup: MockSetUp) -> None:
        # Arrange
        (mock_get_organization_by_id, mock_get_user_by_id, mock_db, mock_logger, mock_user_context, mock_collection) = (
            mock_setup
        )

        mock_user_id = generate_uuid()
        mock_user_context.configure_mock(user_id=mock_user_id)
        mock_invitation_id = generate_uuid()

        mock_invitation = JoinOrganizationInvitationModel(
            _id=mock_invitation_id,
            organization_id=generate_uuid(),
            sender_id=generate_uuid(),
            receiver_id=mock_user_id,
            status=Status.Pending,
            expires_at=get_utc_now(),
            is_read=False,
        )
        mock_invitation_data = mock_invitation.model_dump(by_alias=True)

        mock_collection.configure_mock(find_one=Mock(return_value=mock_invitation_data))
        mock_update_one_result = MockUpdateResult(modified_count=0)
        mock_collection.configure_mock(update_one=Mock(return_value=mock_update_one_result))

        mark_invitation_read_or_unread = MarkInvitationReadOrUnread(
            get_organization_by_id=mock_get_organization_by_id,
            get_user_by_id=mock_get_user_by_id,
            db=mock_db,
            logger=mock_logger,
            user_context=mock_user_context,
        )

        request = MarkInvitationReadOrUnread.Request(invitation_id=mock_invitation_id, is_read=True)

        # Act
        response = await mark_invitation_read_or_unread.aexecute(request)

        # Assert
        assert response.success is False
        mock_logger.error.assert_called_once_with(
            f"Failed to mark invitation is_read True with id {mock_invitation_id}."
        )
        mock_collection.find_one.assert_called_once_with({"_id": mock_invitation_id})
        mock_collection.update_one.assert_called_once()
