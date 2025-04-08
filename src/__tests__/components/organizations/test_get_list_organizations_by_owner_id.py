from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from ....components.organizations.get_list_organizations_by_owner_id import GetOrganizationByOwnerId
from ....exceptions import NotFoundError

MockSetUp = tuple[Mock, Mock, Mock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = AsyncMock()
    mock_user_context = Mock()

    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_user_context, mock_collection


class TestGetOrganizationByOwnerId:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_collection = mock_setup

        # Mock user_context
        user_id = uuid4()
        mock_user_context.configure_mock(user_id=user_id)

        # Mock request and database response
        organization_data = [
            {
                "name": "org_test_1",
                "avatar_url": "http://example.com/avatar_1.png",
                "owner_id": user_id,
            },
            {
                "name": "org_test_2",
                "avatar_url": "http://example.com/avatar_2.png",
                "owner_id": user_id,
            },
            {
                "name": "org_test_3",
                "avatar_url": "http://example.com/avatar_3.png",
                "owner_id": user_id,
            },
        ]
        mock_collection.configure_mock(find=Mock(return_value=organization_data))

        # Initialize the component
        get_organization_by_id = GetOrganizationByOwnerId(
            db=mock_db, logger=mock_logger, user_context=mock_user_context
        )

        # Execute the component
        # request = GetOrganizationByOwnerId.Request(organization_id=organization_id)
        response = await get_organization_by_id.aexecute()

        # Assertions
        # assert response.organizations is not None ## có thể trả về list rỗng?
        assert len(response.organizations) == len(organization_data)
        for org, org_data in zip(response.organizations, organization_data):
            assert org.name == org_data["name"]
            assert org.avatar_url == org_data["avatar_url"]
            assert org.owner_id == user_id

        mock_collection.find.assert_called_once_with({"owner_id": user_id})

    @pytest.mark.asyncio
    async def test_aexecute_when_organization_not_found_throws_not_found_error(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_collection = mock_setup

        # Mock user_context
        user_id = uuid4()  # Use uuid4 to generate a valid UUID object
        mock_user_context.configure_mock(user_id=user_id)
        mock_collection.configure_mock(find=Mock(return_value=None))

        # Initialize the component
        get_organization_by_id = GetOrganizationByOwnerId(
            db=mock_db, logger=mock_logger, user_context=mock_user_context
        )

        # Execute the component
        # request = GetUserById.Request(organizatio÷n_id=organization_id)
        with pytest.raises(NotFoundError):
            await get_organization_by_id.aexecute()

        # Verify interactions
        mock_collection.find.assert_called_once_with({"owner_id": user_id})
