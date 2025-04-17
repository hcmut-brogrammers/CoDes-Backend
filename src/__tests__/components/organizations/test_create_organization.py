from unittest.mock import AsyncMock, Mock, call
from uuid import uuid4

import pytest

from ....common.models import OrganizationModel
from ....components.organizations.create_organization import CreateOrganization
from ....exceptions import InternalServerError

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

        # Mock user_context
        user_id = uuid4()
        mock_user_context.configure_mock(user_id=user_id)

        # Mock request and database response
        organization = OrganizationModel(
            name="org_test",
            avatar_url="http://example.com/avatar.png",
            owner_id=user_id,
        )

        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=organization.id)),
            find_one=Mock(return_value=organization.model_dump(by_alias=True)),
        )

        # Initialize the component
        create_organization = CreateOrganization(db=mock_db, logger=mock_logger, user_context=mock_user_context)

        # Execute the component
        request = CreateOrganization.Request(name=organization.name, avatar_url=organization.avatar_url)
        response = await create_organization.aexecute(request)

        # Assertions
        assert response.created_organization is not None
        assert response.created_organization.owner_id == mock_user_context.user_id
        assert response.created_organization.name == organization.name
        assert response.created_organization.avatar_url == organization.avatar_url

        # Verify interactions
        mock_collection.insert_one.assert_called_once()
        filter = {
            "owner_id": mock_user_context.user_id,
            "is_default": True,
        }
        mock_collection.find_one.call_count == 2
        expect_calls = [call(filter), call({"_id": organization.id})]
        assert mock_collection.find_one.call_args_list == expect_calls
        # mock_collection.find_one.assert_called_once_with(filter)
        # mock_collection.find_one.assert_called_once_with({"_id": organization.id})

    @pytest.mark.asyncio
    async def test_aexecute_when_organizations_not_found_throws_internal_server_error(
        self, mock_setup: MockSetUp
    ) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_collection = mock_setup

        # Mock user_context
        user_id = uuid4()
        mock_user_context.configure_mock(user_id=user_id)

        # Mock request and database response
        organization = OrganizationModel(
            name="org_test",
            avatar_url="http://example.com/avatar.png",
            owner_id=user_id,
        )

        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=organization.id)),
            find_one=Mock(return_value=None),
        )

        # Initialize the component
        create_organization = CreateOrganization(db=mock_db, logger=mock_logger, user_context=mock_user_context)

        # Execute the component
        request = CreateOrganization.Request(
            name=organization.name,
            avatar_url=organization.avatar_url,
        )
        with pytest.raises(InternalServerError):
            await create_organization.aexecute(request)

        # Verify interactions
        mock_collection.insert_one.assert_called_once()
        filter = {
            "owner_id": mock_user_context.user_id,
            "is_default": True,
        }
        mock_collection.find_one.call_count == 2
        expect_calls = [call(filter), call({"_id": organization.id})]
        assert mock_collection.find_one.call_args_list == expect_calls
