from datetime import timedelta
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from ....common.models import (
    InvitationStatus,
    InviteeAction,
    JoinOrganizationInvitationModel,
    JoinOrganizationMember,
    OrganizationModel,
    TakenAction,
    UserModel,
    UserRole,
)
from ....components.join_organization_invitations.accept_or_reject_invitation import AcceptOrRejectInvitation
from ....components.organizations import GetOrganizationById
from ....components.users import AddUserToOrganization, GetUserById
from ....utils.common import generate_uuid, get_utc_now


@pytest.fixture
def mock_sender_id() -> UUID:
    return generate_uuid()


@pytest.fixture
def mock_receiver_id() -> UUID:
    return generate_uuid()


@pytest.fixture
def mock_organization(mock_sender_id: UUID) -> OrganizationModel:
    return OrganizationModel(
        name="Test Organization",
        avatar_url="http://example.com/avatar.png",
        owner_id=mock_sender_id,
        is_default=False,
        members=[
            JoinOrganizationMember(
                member_id=mock_sender_id,
                member_role=UserRole.OrganizationAdmin,
            )
        ],
    )


@pytest.fixture
def mock_receiver(mock_receiver_id: UUID) -> UserModel:
    return UserModel(
        _id=mock_receiver_id,
        email="johndoe@gmail.com",
        username="johndoe",
        hashed_password="hashed_password",
        role=UserRole.OrganizationMember,
    )


@pytest.fixture
def mock_unexpired_invitation(
    mock_sender_id: UUID,
    mock_receiver_id: UUID,
    mock_organization: OrganizationModel,
) -> JoinOrganizationInvitationModel:
    return JoinOrganizationInvitationModel(
        _id=generate_uuid(),
        organization_id=mock_organization.id,
        sender_id=mock_sender_id,
        receiver_id=mock_receiver_id,
        status=InvitationStatus.Pending,
        expires_at=get_utc_now() + timedelta(days=3),
    )


@pytest.fixture
def mock_expired_invitation(
    mock_unexpired_invitation: JoinOrganizationInvitationModel,
) -> JoinOrganizationInvitationModel:
    invitation = mock_unexpired_invitation.model_copy()
    invitation.expires_at = get_utc_now() - timedelta(days=1)
    return invitation


class TestAcceptOrRejectInvitation:
    @pytest.mark.asyncio
    async def test_aexecute_when_accept_should_return_success(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_get_user_by_id: Mock,
        mock_get_organization_by_id: Mock,
        mock_add_user_to_organization: Mock,
        mock_receiver_id: UUID,
        mock_organization: OrganizationModel,
        mock_receiver: UserModel,
        mock_unexpired_invitation: JoinOrganizationInvitationModel,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_receiver_id)

        mock_invitation_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(return_value=mock_invitation_collection))

        mock_invitation_collection.configure_mock(find_one=Mock(return_value=mock_unexpired_invitation.model_dump()))

        mock_organization.members = []
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=GetUserById.Response(user=mock_receiver)))

        mock_add_user_to_organization.configure_mock(aexecute=AsyncMock(return_value=Mock()))

        accept_or_reject_invitation = AcceptOrRejectInvitation(
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            db=mock_db,
            logger=mock_logger,
            add_user_to_organization=mock_add_user_to_organization,
        )

        mock_invitation_id = mock_unexpired_invitation.id
        request = AcceptOrRejectInvitation.Request(invitation_id=mock_invitation_id, action=InviteeAction.Accept)

        # Act
        response = await accept_or_reject_invitation.aexecute(request)

        # Assert
        assert response.success is True
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_organization.id)
        )
        mock_get_user_by_id.aexecute.assert_called_once_with(GetUserById.Request(user_id=mock_receiver_id))
        mock_add_user_to_organization.aexecute.assert_called_once_with(
            AddUserToOrganization.Request(
                organization_id=mock_organization.id,
                user_id=mock_receiver_id,
                role=UserRole.OrganizationMember,
            )
        )
        mock_invitation_collection.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_when_reject_should_return_success(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_get_user_by_id: Mock,
        mock_get_organization_by_id: Mock,
        mock_add_user_to_organization: Mock,
        mock_receiver_id: UUID,
        mock_organization: OrganizationModel,
        mock_receiver: UserModel,
        mock_unexpired_invitation: JoinOrganizationInvitationModel,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_receiver_id)

        mock_invitation_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(return_value=mock_invitation_collection))

        mock_invitation_collection.configure_mock(find_one=Mock(return_value=mock_unexpired_invitation.model_dump()))

        mock_organization.members = []
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=GetUserById.Response(user=mock_receiver)))

        accept_or_reject_invitation = AcceptOrRejectInvitation(
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            db=mock_db,
            logger=mock_logger,
            add_user_to_organization=mock_add_user_to_organization,
        )

        mock_invitation_id = mock_unexpired_invitation.id
        request = AcceptOrRejectInvitation.Request(invitation_id=mock_invitation_id, action=InviteeAction.Reject)

        # Act
        response = await accept_or_reject_invitation.aexecute(request)

        # Assert
        assert response.success is True
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_organization.id)
        )
        mock_get_user_by_id.aexecute.assert_called_once_with(GetUserById.Request(user_id=mock_receiver_id))
        mock_invitation_collection.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_when_invitation_not_found_should_return_failure(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_get_user_by_id: Mock,
        mock_get_organization_by_id: Mock,
        mock_add_user_to_organization: Mock,
        mock_receiver_id: UUID,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_receiver_id)

        mock_invitation_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(return_value=mock_invitation_collection))

        # Simulate no invitation found
        mock_invitation_collection.configure_mock(find_one=Mock(return_value=None))

        accept_or_reject_invitation = AcceptOrRejectInvitation(
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            db=mock_db,
            logger=mock_logger,
            add_user_to_organization=mock_add_user_to_organization,
        )

        mock_invitation_id = generate_uuid()
        request = AcceptOrRejectInvitation.Request(invitation_id=mock_invitation_id, action=InviteeAction.Accept)

        # Act
        response = await accept_or_reject_invitation.aexecute(request)

        # Assert
        assert response.success is False
        mock_invitation_collection.find_one.assert_called_once_with({"_id": mock_invitation_id})

    @pytest.mark.asyncio
    async def test_aexecute_when_invitation_expired_should_return_failure(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_get_user_by_id: Mock,
        mock_get_organization_by_id: Mock,
        mock_add_user_to_organization: Mock,
        mock_receiver_id: UUID,
        mock_expired_invitation: JoinOrganizationInvitationModel,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_receiver_id)

        mock_invitation_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(return_value=mock_invitation_collection))
        mock_invitation_collection.configure_mock(find_one=Mock(return_value=mock_expired_invitation.model_dump()))

        accept_or_reject_invitation = AcceptOrRejectInvitation(
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            db=mock_db,
            logger=mock_logger,
            add_user_to_organization=mock_add_user_to_organization,
        )

        mock_invitation_id = mock_expired_invitation.id
        request = AcceptOrRejectInvitation.Request(invitation_id=mock_invitation_id, action=InviteeAction.Accept)

        # Act
        response = await accept_or_reject_invitation.aexecute(request)

        # Assert
        assert response.success is False
        mock_invitation_collection.find_one.assert_called_once_with({"_id": mock_invitation_id})

    @pytest.mark.asyncio
    async def test_aexecute_when_user_not_authorized_should_return_failure(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_get_user_by_id: Mock,
        mock_get_organization_by_id: Mock,
        mock_add_user_to_organization: Mock,
        mock_unexpired_invitation: JoinOrganizationInvitationModel,
    ) -> None:
        # Arrange
        # Simulate a different user trying to accept/reject the invitation
        mock_unauthorized_user_id = generate_uuid()
        mock_user_context.configure_mock(user_id=mock_unauthorized_user_id)

        mock_invitation_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(return_value=mock_invitation_collection))
        mock_invitation_collection.configure_mock(find_one=Mock(return_value=mock_unexpired_invitation.model_dump()))

        accept_or_reject_invitation = AcceptOrRejectInvitation(
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            db=mock_db,
            logger=mock_logger,
            add_user_to_organization=mock_add_user_to_organization,
        )

        mock_invitation_id = mock_unexpired_invitation.id
        request = AcceptOrRejectInvitation.Request(invitation_id=mock_invitation_id, action=InviteeAction.Accept)

        # Act
        response = await accept_or_reject_invitation.aexecute(request)

        # Assert
        assert response.success is False
        mock_invitation_collection.find_one.assert_called_once_with({"_id": mock_invitation_id})

    @pytest.mark.asyncio
    async def test_aexecute_when_no_organization_found_should_return_failure(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_get_organization_by_id: Mock,
        mock_get_user_by_id: Mock,
        mock_add_user_to_organization: Mock,
        mock_receiver_id: UUID,
        mock_unexpired_invitation: JoinOrganizationInvitationModel,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_receiver_id)

        mock_invitation_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(return_value=mock_invitation_collection))
        mock_invitation_collection.configure_mock(find_one=Mock(return_value=mock_unexpired_invitation.model_dump()))

        # Simulate no organization found
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=None))
        )

        accept_or_reject_invitation = AcceptOrRejectInvitation(
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            db=mock_db,
            logger=mock_logger,
            add_user_to_organization=mock_add_user_to_organization,
        )

        mock_invitation_id = mock_unexpired_invitation.id
        request = AcceptOrRejectInvitation.Request(invitation_id=mock_invitation_id, action=InviteeAction.Accept)

        # Act
        response = await accept_or_reject_invitation.aexecute(request)

        # Assert
        assert response.success is False
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_unexpired_invitation.organization_id)
        )

    @pytest.mark.asyncio
    async def test_aexecute_when_no_user_found_should_return_failure(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_get_organization_by_id: Mock,
        mock_get_user_by_id: Mock,
        mock_add_user_to_organization: Mock,
        mock_receiver_id: UUID,
        mock_unexpired_invitation: JoinOrganizationInvitationModel,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_receiver_id)

        mock_invitation_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(return_value=mock_invitation_collection))
        mock_invitation_collection.configure_mock(find_one=Mock(return_value=mock_unexpired_invitation.model_dump()))

        # Simulate no user found
        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=GetUserById.Response(user=None)))

        accept_or_reject_invitation = AcceptOrRejectInvitation(
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            db=mock_db,
            logger=mock_logger,
            add_user_to_organization=mock_add_user_to_organization,
        )

        mock_invitation_id = mock_unexpired_invitation.id
        request = AcceptOrRejectInvitation.Request(invitation_id=mock_invitation_id, action=InviteeAction.Accept)

        # Act
        response = await accept_or_reject_invitation.aexecute(request)

        # Assert
        assert response.success is False
        mock_get_user_by_id.aexecute.assert_called_once_with(
            GetUserById.Request(user_id=mock_unexpired_invitation.receiver_id)
        )

    @pytest.mark.asyncio
    async def test_aexecute_when_cannot_add_user_to_organization_should_return_failure(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_get_organization_by_id: Mock,
        mock_get_user_by_id: Mock,
        mock_add_user_to_organization: Mock,
        mock_receiver_id: UUID,
        mock_unexpired_invitation: JoinOrganizationInvitationModel,
        mock_organization: OrganizationModel,
        mock_receiver: UserModel,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_receiver_id)

        mock_invitation_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(return_value=mock_invitation_collection))
        mock_invitation_collection.configure_mock(find_one=Mock(return_value=mock_unexpired_invitation.model_dump()))

        mock_organization.members = []
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=GetUserById.Response(user=mock_receiver)))

        # Simulate failure to add user to organization
        mock_add_user_to_organization.configure_mock(aexecute=AsyncMock(return_value=None))

        accept_or_reject_invitation = AcceptOrRejectInvitation(
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            db=mock_db,
            logger=mock_logger,
            add_user_to_organization=mock_add_user_to_organization,
        )

        mock_invitation_id = mock_unexpired_invitation.id
        request = AcceptOrRejectInvitation.Request(invitation_id=mock_invitation_id, action=InviteeAction.Accept)

        # Act
        response = await accept_or_reject_invitation.aexecute(request)

        # Assert
        assert response.success is False
        mock_add_user_to_organization.aexecute.assert_called_once_with(
            AddUserToOrganization.Request(
                organization_id=mock_organization.id,
                user_id=mock_receiver_id,
                role=UserRole.OrganizationMember,
            )
        )

    @pytest.mark.asyncio
    async def test_aexecute_when_receiver_already_in_members_list_should_return_failure(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_get_organization_by_id: Mock,
        mock_get_user_by_id: Mock,
        mock_add_user_to_organization: Mock,
        mock_receiver_id: UUID,
        mock_unexpired_invitation: JoinOrganizationInvitationModel,
        mock_organization: OrganizationModel,
        mock_receiver: UserModel,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_receiver_id)

        mock_invitation_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(return_value=mock_invitation_collection))
        mock_invitation_collection.configure_mock(find_one=Mock(return_value=mock_unexpired_invitation.model_dump()))

        # Simulate organization where the receiver is already a member
        mock_organization.members = [
            JoinOrganizationMember(member_id=mock_receiver_id, member_role=UserRole.OrganizationMember)
        ]
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=GetUserById.Response(user=mock_receiver)))

        accept_or_reject_invitation = AcceptOrRejectInvitation(
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            db=mock_db,
            logger=mock_logger,
            add_user_to_organization=mock_add_user_to_organization,
        )

        mock_invitation_id = mock_unexpired_invitation.id
        request = AcceptOrRejectInvitation.Request(invitation_id=mock_invitation_id, action=InviteeAction.Accept)

        # Act
        response = await accept_or_reject_invitation.aexecute(request)

        # Assert
        assert response.success is False
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_organization.id)
        )
        mock_get_user_by_id.aexecute.assert_called_once_with(GetUserById.Request(user_id=mock_receiver_id))
        mock_add_user_to_organization.aexecute.assert_not_called()
        mock_invitation_collection.update_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_aexecute_when_invitation_status_not_pending_should_return_failure(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_get_organization_by_id: Mock,
        mock_get_user_by_id: Mock,
        mock_add_user_to_organization: Mock,
        mock_receiver_id: UUID,
        mock_unexpired_invitation: JoinOrganizationInvitationModel,
        mock_organization: OrganizationModel,
        mock_receiver: UserModel,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_receiver_id)

        # Simulate an invitation with a status other than Pending
        non_pending_invitation = mock_unexpired_invitation.model_copy()
        non_pending_invitation.status = InvitationStatus.Completed

        mock_invitation_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(return_value=mock_invitation_collection))
        mock_invitation_collection.configure_mock(find_one=Mock(return_value=non_pending_invitation.model_dump()))

        accept_or_reject_invitation = AcceptOrRejectInvitation(
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            db=mock_db,
            logger=mock_logger,
            add_user_to_organization=mock_add_user_to_organization,
        )

        mock_invitation_id = non_pending_invitation.id
        request = AcceptOrRejectInvitation.Request(invitation_id=mock_invitation_id, action=InviteeAction.Accept)

        # Act
        response = await accept_or_reject_invitation.aexecute(request)

        # Assert
        assert response.success is False
        mock_invitation_collection.find_one.assert_called_once_with({"_id": mock_invitation_id})
        mock_get_organization_by_id.aexecute.assert_not_called()
        mock_get_user_by_id.aexecute.assert_not_called()
        mock_add_user_to_organization.aexecute.assert_not_called()

    @pytest.mark.asyncio
    async def test_aexecute_when_invitation_already_has_taken_action_should_return_failure(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_get_organization_by_id: Mock,
        mock_get_user_by_id: Mock,
        mock_add_user_to_organization: Mock,
        mock_receiver_id: UUID,
        mock_unexpired_invitation: JoinOrganizationInvitationModel,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_receiver_id)

        # Simulate an invitation that already has a taken_action
        invitation_with_taken_action = mock_unexpired_invitation.model_copy()
        invitation_with_taken_action.taken_action = TakenAction(
            action=InviteeAction.Accept,
            taken_at=get_utc_now(),
        )

        mock_invitation_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(return_value=mock_invitation_collection))
        mock_invitation_collection.configure_mock(find_one=Mock(return_value=invitation_with_taken_action.model_dump()))

        accept_or_reject_invitation = AcceptOrRejectInvitation(
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            db=mock_db,
            logger=mock_logger,
            add_user_to_organization=mock_add_user_to_organization,
        )

        mock_invitation_id = invitation_with_taken_action.id
        request = AcceptOrRejectInvitation.Request(invitation_id=mock_invitation_id, action=InviteeAction.Accept)

        # Act
        response = await accept_or_reject_invitation.aexecute(request)

        # Assert
        assert response.success is False
        mock_invitation_collection.find_one.assert_called_once_with({"_id": mock_invitation_id})
        mock_get_organization_by_id.aexecute.assert_not_called()
        mock_get_user_by_id.aexecute.assert_not_called()
        mock_add_user_to_organization.aexecute.assert_not_called()
