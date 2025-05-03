from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest

from ....components.organizations.get_user_default_organization import GetUserDefaultOrganization
from ....exceptions import NotFoundError

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
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        # Mock user_context
        mock_user_id = UUID("9fa24e8e-c58e-44d6-8de0-3c34e8bcbcae")
        mock_organization_id = UUID("b1c345d0-3e8f-4c70-b6f3-843ab6b0df59")

        # Mock database response
        organization_data = {
            "_id": mock_organization_id,
            "name": "org_test_1",
            "avatar_url": "http://example.com/avatar_1.png",
            "owner_id": mock_user_id,
            "is_default": True,
        }

        mock_collection.configure_mock(find_one=Mock(return_value=organization_data))

        # Initialize the component
        get_organization_by_id = GetUserDefaultOrganization(db=mock_db, logger=mock_logger)

        # Execute the component
        get_organization_by_id = GetUserDefaultOrganization(db=mock_db, logger=mock_logger)
        request = GetUserDefaultOrganization.Request(owner_id=mock_user_id)
        response = await get_organization_by_id.aexecute(request)

        # Assertions
        assert response.organization.id == organization_data["_id"]
        assert response.organization.name == organization_data["name"]
        assert response.organization.avatar_url == organization_data["avatar_url"]
        assert response.organization.owner_id == organization_data["owner_id"]
        assert response.organization.is_default == True  # must be True value due to being default org

        # Verify interactions
        mock_collection.find_one.assert_called_once_with({"owner_id": mock_user_id, "is_default": True})

    @pytest.mark.asyncio
    async def test_aexecute_no_organization_found_with_id_throw_exception(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        # # Mock user_context
        mock_user_id = UUID("b1c345d0-3e8f-4c70-b6f3-843ab6b0df59")

        mock_collection.configure_mock(find_one=Mock(return_value=None))

        # Initialize the component
        get_organization_by_id = GetUserDefaultOrganization(db=mock_db, logger=mock_logger)

        # Execute the component with expected Error
        request = GetUserDefaultOrganization.Request(owner_id=mock_user_id)
        with pytest.raises(NotFoundError):
            await get_organization_by_id.aexecute(request)

        # Assertions
        # Verify interactions
        mock_collection.find_one.assert_called_once_with({"owner_id": mock_user_id, "is_default": True})
