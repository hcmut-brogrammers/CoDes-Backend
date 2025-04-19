from typing import Dict
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from pydantic import HttpUrl

from ....common.models import OrganizationModel
from ....components.organizations.update_organization import UpdateOrganization
from ....exceptions import BadRequestError, InternalServerError, NotFoundError

MockSetUp = tuple[Mock, Mock, Mock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_user_context = Mock()
    mock_collection = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_user_context, mock_collection


class TestUpdateOrganization:
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

        update_data = {"name": "update_name", "avatar_url": "http://example.com/avatar.png/update"}
        mock_update_organization = organization.model_copy(update=update_data)
        mock_collection.configure_mock(
            update_one=Mock(return_value=None), find_one=Mock(return_value=organization.model_dump(by_alias=True))
        )

        # Initialize the component
        update_organization = UpdateOrganization(db=mock_db, logger=mock_logger, user_context=mock_user_context)

        # Execute the component
        request = UpdateOrganization.Request(organization_id=organization.id, **update_data)
        response = await update_organization.aexecute(request)

        # Assertions
        assert response.updated_organization is not None
        assert response.updated_organization.id == mock_update_organization.id
        assert response.updated_organization.name == mock_update_organization.name
        assert response.updated_organization.avatar_url == mock_update_organization.avatar_url
        assert response.updated_organization.owner_id == mock_user_context.user_id
        assert response.updated_organization.is_default == organization.is_default

        # Verify interactions
        mock_collection.update_one.assert_called_once()
        mock_collection.find_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_when_no_update_data_from_request_throws_bad_request(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_collection = mock_setup

        # Mock user_context
        user_id = uuid4()
        mock_user_context.configure_mock(user_id=user_id)

        # Mock request and database response
        organization_id = uuid4()
        update_data = {}

        # Initialize the component
        update_organization = UpdateOrganization(db=mock_db, logger=mock_logger, user_context=mock_user_context)

        # Execute the component
        request = UpdateOrganization.Request(organization_id=organization_id, **update_data)
        with pytest.raises(BadRequestError):
            await update_organization.aexecute(request)

    @pytest.mark.asyncio
    async def test_aexecute_when_organization_not_found_throws_not_found_error(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_collection = mock_setup

        # Mock user_context
        user_id = uuid4()
        mock_user_context.configure_mock(user_id=user_id)

        # Mock request and database response
        organization_id = uuid4()

        update_data = {"name": "update_name", "avatar_url": "http://example.com/avatar.png/update"}
        mock_collection.configure_mock(find_one=Mock(return_value=None))

        # Initialize the component
        update_organization = UpdateOrganization(db=mock_db, logger=mock_logger, user_context=mock_user_context)

        # Execute the component
        request = UpdateOrganization.Request(organization_id=organization_id, **update_data)
        with pytest.raises(NotFoundError):
            await update_organization.aexecute(request)
