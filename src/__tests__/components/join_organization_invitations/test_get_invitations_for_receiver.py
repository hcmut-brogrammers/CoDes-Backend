from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from ....common.models.join_organization_invitation import InviteeAction, Status
from ....components.join_workspace_invitations import GetInvitationsForReceiver
from ....exceptions import NotFoundError
from ...utils.common import get_utc_now, get_utc_shifted_from

MockSetUp = tuple[Mock, Mock, Mock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = AsyncMock()
    mock_user_context = Mock()

    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_user_context, mock_collection


class TestGetInvitationsForReceiver:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_collection = mock_setup

        # Mock user_context
        organization_id, sender_id, receiver_id = uuid4(), uuid4(), uuid4()
        mock_user_context.configure_mock(organization_id=organization_id, user_id=receiver_id)

        # Mock database response
        time_now = get_utc_now()
        expires_at = get_utc_shifted_from(time_now, False, 0, 1, 0, 0)
        taken_at = get_utc_shifted_from(expires_at, False, 3, 0, 0, 0)
        invitations_data = [
            {
                "organization_id": organization_id,
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "status": Status.pending,
                "taken_action": None,
                "taken_at": taken_at,
                "expires_at": expires_at,
            },
        ]

        mock_collection.configure_mock(find=Mock(return_value=invitations_data))

        # Initialize the component
        get_invitations_for_receiver = GetInvitationsForReceiver(
            db=mock_db, logger=mock_logger, user_context=mock_user_context
        )

        # Execute the component
        response = await get_invitations_for_receiver.aexecute()

        # Assertions
        assert len(response.invitations) == len(invitations_data)
        for invitation in response.invitations:
            assert invitation.organization_id == mock_user_context.organization_id
            # assert invitation.sender_id == sender_id
            assert invitation.receiver_id == mock_user_context.user_id
            assert invitation.status == Status.pending
            assert invitation.taken_action == None

        # Verify interactions
        filter = {
            "receiver_id": receiver_id,
            "taken_action": None,
            "expires_at": {"$gt": get_utc_now()},
        }
        # mock_collection.find.assert_called_once()
        # mock_collection.find.assert_called_once_with(filter)

        assert mock_collection.find.call_count == 1

        # ✅ Extract the actual argument
        # ✅ Retrieve the called dict
        called_arg = mock_collection.find.call_args[0][0]

        # assert called_arg["receiver_id"] == mock_user_context.user_id
        # assert called_arg["taken_action"] == None
        # assert type(called_arg["expires_at"]["$gt"]) is datetime

        # ✅ Assert only subset
        expected = {"receiver_id": receiver_id, "taken_action": None}

        ## same as
        # set(expected.items()).issubset(set(called_arg.items()))
        assert expected.items() <= called_arg.items()
