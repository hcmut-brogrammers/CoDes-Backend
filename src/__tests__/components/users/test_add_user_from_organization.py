from unittest.mock import Mock

import pytest

from ....common.models import JoinedOrganization, JoinOrganizationMember, UserRole
from ....components.users import AddUserToOrganization
from ....utils.common import generate_uuid


class TestAddUserFromOrganization:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_db: Mock, mock_logger: Mock) -> None:
        # Arrange
        mock_user_collection = Mock()
        mock_organization_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(side_effect=[mock_user_collection, mock_organization_collection]))

        mock_user_collection.configure_mock(update_one=Mock(return_value=Mock(modified_count=1)))
        mock_organization_collection.configure_mock(update_one=Mock(return_value=Mock(modified_count=1)))
        mock_organization_id = generate_uuid()
        mock_user_id = generate_uuid()
        request = AddUserToOrganization.Request(
            organization_id=mock_organization_id, user_id=mock_user_id, role=UserRole.OrganizationAdmin
        )
        add_user_from_organization = AddUserToOrganization(db=mock_db, logger=mock_logger)

        # Act
        response = await add_user_from_organization.aexecute(request)

        # Assert
        assert response is not None
        assert response.joined_organization.organization_id == mock_organization_id
        assert response.joined_organization.role == UserRole.OrganizationAdmin
        assert response.joined_organization.joined_at is not None

        assert response.join_organization_member.member_id == mock_user_id
        assert response.join_organization_member.member_role == UserRole.OrganizationAdmin
        assert response.join_organization_member.joined_at is not None

        mock_user_collection.update_one.assert_called_once()
        mock_organization_collection.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_when_not_update_user_should_return_empty(self, mock_db: Mock, mock_logger: Mock) -> None:
        # Arrange
        mock_user_collection = Mock()
        mock_organization_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(side_effect=[mock_user_collection, mock_organization_collection]))

        mock_user_collection.configure_mock(update_one=Mock(return_value=Mock(modified_count=0)))
        mock_organization_id = generate_uuid()
        mock_user_id = generate_uuid()
        request = AddUserToOrganization.Request(
            organization_id=mock_organization_id, user_id=mock_user_id, role=UserRole.OrganizationAdmin
        )
        add_user_from_organization = AddUserToOrganization(db=mock_db, logger=mock_logger)

        # Act
        response = await add_user_from_organization.aexecute(request)

        # Assert
        assert response is None
        mock_user_collection.update_one.assert_called_once()
        mock_organization_collection.update_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_aexecute_when_not_update_organization_should_return_empty(
        self, mock_db: Mock, mock_logger: Mock
    ) -> None:
        # Arrange
        mock_user_collection = Mock()
        mock_organization_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(side_effect=[mock_user_collection, mock_organization_collection]))

        mock_user_collection.configure_mock(update_one=Mock(return_value=Mock(modified_count=1)))
        mock_organization_collection.configure_mock(update_one=Mock(return_value=Mock(modified_count=0)))
        mock_organization_id = generate_uuid()
        mock_user_id = generate_uuid()
        request = AddUserToOrganization.Request(
            organization_id=mock_organization_id, user_id=mock_user_id, role=UserRole.OrganizationAdmin
        )
        remove_user_from_organization = AddUserToOrganization(db=mock_db, logger=mock_logger)

        # Act
        response = await remove_user_from_organization.aexecute(request)

        # Assert
        assert response is None
        mock_user_collection.update_one.assert_called_once()
        mock_organization_collection.update_one.assert_called_once()
