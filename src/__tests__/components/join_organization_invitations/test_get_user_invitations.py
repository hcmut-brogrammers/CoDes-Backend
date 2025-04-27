from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from ....common.models import JoinOrganizationInvitationModel, OrganizationModel, UserModel
from ....components.join_organization_invitations import GetUserInvitations
from ....components.organizations import GetOrganizationById
from ....components.users import GetUserById
from ...utils.common import generate_uuid, get_utc_now


@pytest.fixture
def mock_invitation() -> JoinOrganizationInvitationModel:
    organization_id = generate_uuid()
    sender_id = generate_uuid()
    receiver_id = generate_uuid()

    invitation = JoinOrganizationInvitationModel(
        organization_id=organization_id,
        sender_id=sender_id,
        receiver_id=receiver_id,
        expires_at=get_utc_now() + timedelta(days=3),
    )
    return invitation


class TestGetUserInvitations:
    @pytest.mark.asyncio
    async def test_aexecute_success(
        self,
        mock_get_organization_by_id: Mock,
        mock_get_user_by_id: Mock,
        mock_db: Mock,
        mock_collection: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_invitation: JoinOrganizationInvitationModel,
    ) -> None:
        # Arrange
        mock_organization_id = mock_invitation.organization_id
        mock_sender_id = mock_invitation.sender_id
        mock_receiver_id = mock_invitation.receiver_id

        mock_invitations = [mock_invitation]
        mock_invitations_data = [invitation.model_dump(by_alias=True) for invitation in mock_invitations]
        mock_collection.configure_mock(find=Mock(return_value=mock_invitations_data))
        mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))

        mock_organization = OrganizationModel(
            _id=mock_organization_id,
            name="Test Organization",
            avatar_url="http://example.com/avatar.png",
            owner_id=mock_sender_id,
        )
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        mock_user = UserModel(
            _id=mock_sender_id,
            username="sender",
            email="sender@gmail.com",
            hashed_password="hashed_password",
        )
        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=GetUserById.Response(user=mock_user)))

        mock_user_context.configure_mock(user_id=mock_receiver_id)

        # Act
        get_user_invitations = GetUserInvitations(
            get_organization_by_id=mock_get_organization_by_id,
            get_user_by_id=mock_get_user_by_id,
            db=mock_db,
            logger=mock_logger,
            user_context=mock_user_context,
        )
        response = await get_user_invitations.aexecute()

        # Assert
        assert response.invitations is not None
        assert len(response.invitations) == len(mock_invitations)

        invitation = response.invitations[0]
        assert invitation.id == mock_invitation.id
        assert invitation.organization.name == mock_organization.name
        assert invitation.sender.username == mock_user.username
        assert invitation.status == mock_invitation.status
        assert invitation.expires_at == mock_invitation.expires_at
        assert invitation.created_at == mock_invitation.created_at

        mock_collection.find.assert_called_once()
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_organization_id)
        )
        mock_get_user_by_id.aexecute.assert_called_once_with(GetUserById.Request(user_id=mock_sender_id))

    @pytest.mark.asyncio
    async def test_aexecute_with_organization_not_found(
        self,
        mock_get_organization_by_id: Mock,
        mock_get_user_by_id: Mock,
        mock_db: Mock,
        mock_collection: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_invitation: JoinOrganizationInvitationModel,
    ) -> None:
        # Arrange
        mock_organization_id = mock_invitation.organization_id
        mock_receiver_id = mock_invitation.receiver_id

        mock_invitations = [mock_invitation]
        mock_invitations_data = [invitation.model_dump(by_alias=True) for invitation in mock_invitations]
        mock_collection.configure_mock(find=Mock(return_value=mock_invitations_data))
        mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))

        # Simulate organization not found
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=None))
        )

        mock_user_context.configure_mock(user_id=mock_receiver_id)

        # Act
        get_user_invitations = GetUserInvitations(
            get_organization_by_id=mock_get_organization_by_id,
            get_user_by_id=mock_get_user_by_id,
            db=mock_db,
            logger=mock_logger,
            user_context=mock_user_context,
        )
        response = await get_user_invitations.aexecute()

        # Assert
        assert response.invitations is not None
        assert len(response.invitations) == 0

        mock_collection.find.assert_called_once()
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_organization_id)
        )
        mock_logger.error.assert_called_once_with(f"Organization with id {mock_organization_id} not found.")
        mock_get_user_by_id.aexecute.assert_not_called()

    @pytest.mark.asyncio
    async def test_aexecute_with_user_not_found(
        self,
        mock_get_organization_by_id: Mock,
        mock_get_user_by_id: Mock,
        mock_db: Mock,
        mock_collection: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_invitation: JoinOrganizationInvitationModel,
    ):
        # Arrange
        mock_organization_id = mock_invitation.organization_id
        mock_sender_id = mock_invitation.sender_id
        mock_receiver_id = mock_invitation.receiver_id

        mock_invitations = [mock_invitation]
        mock_invitations_data = [invitation.model_dump(by_alias=True) for invitation in mock_invitations]
        mock_collection.configure_mock(find=Mock(return_value=mock_invitations_data))
        mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))

        mock_organization = OrganizationModel(
            _id=mock_organization_id,
            name="Test Organization",
            avatar_url="http://example.com/avatar.png",
            owner_id=mock_sender_id,
        )
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        # Simulate user not found
        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=GetUserById.Response(user=None)))

        mock_user_context.configure_mock(user_id=mock_receiver_id)

        # Act
        get_user_invitations = GetUserInvitations(
            get_organization_by_id=mock_get_organization_by_id,
            get_user_by_id=mock_get_user_by_id,
            db=mock_db,
            logger=mock_logger,
            user_context=mock_user_context,
        )
        response = await get_user_invitations.aexecute()

        # Assert
        assert response.invitations is not None
        assert len(response.invitations) == 0

        mock_collection.find.assert_called_once()
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_organization_id)
        )
        mock_get_user_by_id.aexecute.assert_called_once_with(GetUserById.Request(user_id=mock_sender_id))
        mock_logger.error.assert_called_once_with(f"User with id {mock_sender_id} not found.")
