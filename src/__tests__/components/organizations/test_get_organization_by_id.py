from unittest.mock import AsyncMock, Mock

import pytest

from ....common.models import OrganizationModel
from ....components.organizations.get_organization_by_id import GetOrganizationById
from ....utils.common import generate_uuid

MockSetUp = tuple[Mock, Mock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = AsyncMock()

    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_collection


class TestGetOrganizationByOwnerId:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_setup: MockSetUp) -> None:
        # Arrange
        mock_db, mock_logger, mock_collection = mock_setup

        mock_user_id = generate_uuid()
        mock_organization_id = generate_uuid()

        mock_organization = OrganizationModel(
            _id=mock_organization_id,
            name="org_test_1",
            avatar_url="http://example.com/avatar_1.png",
            owner_id=mock_user_id,
            is_default=False,
        )
        mock_organization_data = mock_organization.model_dump(by_alias=True)
        mock_collection.configure_mock(find_one=Mock(return_value=mock_organization_data))

        get_organization_by_id = GetOrganizationById(db=mock_db, logger=mock_logger)
        get_organization_by_id = GetOrganizationById(db=mock_db, logger=mock_logger)
        request = GetOrganizationById.Request(id=mock_organization_id)

        # Act
        response = await get_organization_by_id.aexecute(request)

        # Assert
        assert response.organization is not None
        assert response.organization.id == mock_organization_id
        assert response.organization.name == mock_organization.name
        assert response.organization.avatar_url == mock_organization.avatar_url
        assert response.organization.owner_id == mock_user_id
        assert response.organization.is_default == mock_organization.is_default

        # Verify interactions
        mock_collection.find_one.assert_called_once_with({"_id": mock_organization_id})

    @pytest.mark.asyncio
    async def test_aexecute_no_organization_found_with_id_throw_exception(self, mock_setup: MockSetUp) -> None:
        # Arrange
        mock_db, mock_logger, mock_collection = mock_setup
        mock_organization_id = generate_uuid()
        mock_collection.configure_mock(find_one=Mock(return_value=None))
        get_organization_by_id = GetOrganizationById(db=mock_db, logger=mock_logger)

        request = GetOrganizationById.Request(id=mock_organization_id)

        # Act
        response = await get_organization_by_id.aexecute(request)

        # Assert
        assert response.organization is None
