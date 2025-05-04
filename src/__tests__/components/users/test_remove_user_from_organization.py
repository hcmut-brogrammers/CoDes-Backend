from unittest.mock import Mock

import pytest

from ....components.users import RemoveUserFromOrganization
from ....utils.common import generate_uuid


class TestRemoveUserFromOrganization:
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
        request = RemoveUserFromOrganization.Request(organization_id=mock_organization_id, user_id=mock_user_id)
        remove_user_from_organization = RemoveUserFromOrganization(db=mock_db, logger=mock_logger)

        # Act
        response = await remove_user_from_organization.aexecute(request)

        # Assert
        assert response is not None
        assert response.success is True
        mock_user_collection.update_one.assert_called_once_with(
            {"_id": mock_user_id}, {"$pull": {"joined_organizations": {"organization_id": mock_organization_id}}}
        )
        mock_organization_collection.update_one.assert_called_once_with(
            {"_id": mock_organization_id}, {"$pull": {"members": {"member_id": mock_user_id}}}
        )

    @pytest.mark.asyncio
    async def test_aexecute_when_not_update_user_should_return_empty(self, mock_db: Mock, mock_logger: Mock) -> None:
        # Arrange
        mock_user_collection = Mock()
        mock_organization_collection = Mock()
        mock_db.configure_mock(get_collection=Mock(side_effect=[mock_user_collection, mock_organization_collection]))

        mock_user_collection.configure_mock(update_one=Mock(return_value=Mock(modified_count=0)))
        mock_organization_id = generate_uuid()
        mock_user_id = generate_uuid()
        request = RemoveUserFromOrganization.Request(organization_id=mock_organization_id, user_id=mock_user_id)
        remove_user_from_organization = RemoveUserFromOrganization(db=mock_db, logger=mock_logger)

        # Act
        response = await remove_user_from_organization.aexecute(request)

        # Assert
        assert response is None
        mock_user_collection.update_one.assert_called_once_with(
            {"_id": mock_user_id}, {"$pull": {"joined_organizations": {"organization_id": mock_organization_id}}}
        )
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
        request = RemoveUserFromOrganization.Request(organization_id=mock_organization_id, user_id=mock_user_id)
        remove_user_from_organization = RemoveUserFromOrganization(db=mock_db, logger=mock_logger)

        # Act
        response = await remove_user_from_organization.aexecute(request)

        # Assert
        assert response is None
        mock_user_collection.update_one.assert_called_once_with(
            {"_id": mock_user_id}, {"$pull": {"joined_organizations": {"organization_id": mock_organization_id}}}
        )
        mock_organization_collection.update_one.assert_called_once_with(
            {"_id": mock_organization_id}, {"$pull": {"members": {"member_id": mock_user_id}}}
        )
