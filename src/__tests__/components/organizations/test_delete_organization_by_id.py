from typing import Dict
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from pydantic import HttpUrl

from src.utils.common import get_utc_now

from ....common.models import OrganizationModel
from ....components.organizations.delete_organization_by_id import DeleteOrganizationById
from ....exceptions import BadRequestError, NotFoundError

MockSetUp = tuple[Mock, Mock, Mock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_user_context = Mock()
    mock_collection = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_user_context, mock_collection


class TestDeleteOrganizationById:
    @pytest.mark.asyncio
    async def test_aexecute_success_with_is_default_is_False(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_collection = mock_setup

        # Mock user_context
        user_id = uuid4()
        mock_user_context.configure_mock(user_id=user_id)

        # Mock request and database response
        organization = OrganizationModel(
            name="org_test", avatar_url="http://example.com/avatar.png", owner_id=user_id, is_default=False
        )

        delete_data = {"is_deleted": True}
        mock_delete_organization = organization.model_copy(update=delete_data)
        mock_collection.configure_mock(
            update_one=Mock(return_vaulue=None), find_one=Mock(return_value=organization.model_dump(by_alias=True))
        )

        # Initialize the component
        delete_organization = DeleteOrganizationById(db=mock_db, logger=mock_logger, user_context=mock_user_context)

        # Execute the component
        request = DeleteOrganizationById.Request(organization_id=organization.id)
        response = await delete_organization.aexecute(request)

        # Assertions
        assert response.deleted_organization is not None
        assert response.deleted_organization.is_deleted == mock_delete_organization.is_deleted
        assert response.deleted_organization.is_default == mock_delete_organization.is_default
        assert response.deleted_organization.id == mock_delete_organization.id
        assert response.deleted_organization.name == mock_delete_organization.name
        assert response.deleted_organization.avatar_url == mock_delete_organization.avatar_url
        assert response.deleted_organization.owner_id == mock_user_context.user_id
        assert response.deleted_organization.is_default == organization.is_default

        # Verify interactions
        mock_collection.update_one.assert_called_once()
        mock_collection.find_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_when_organization_is_default_throws_bad_request(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_collection = mock_setup

        # Mock user_context
        user_id = uuid4()
        mock_user_context.configure_mock(user_id=user_id)

        # Mock request and database response
        organization = OrganizationModel(
            name="org_test", avatar_url="http://example.com/avatar.png", owner_id=user_id, is_default=True
        )

        mock_collection.configure_mock(find_one=Mock(return_value=organization.model_dump(by_alias=True)))

        # Initialize the component
        delete_organization = DeleteOrganizationById(db=mock_db, logger=mock_logger, user_context=mock_user_context)

        # Execute the component
        request = DeleteOrganizationById.Request(organization_id=organization.id)
        with pytest.raises(BadRequestError):
            await delete_organization.aexecute(request)

    @pytest.mark.asyncio
    async def test_aexecute_when_organization_not_found_throws_not_found_error(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_user_context, mock_collection = mock_setup

        # Mock user_context
        user_id = uuid4()
        mock_user_context.configure_mock(user_id=user_id)

        # Mock request and database response
        organization_id = uuid4()

        mock_collection.configure_mock(find_one=Mock(return_value=None))

        # Initialize the component
        delete_organization = DeleteOrganizationById(db=mock_db, logger=mock_logger, user_context=mock_user_context)

        # Execute the component
        request = DeleteOrganizationById.Request(organization_id=organization_id)
        with pytest.raises(NotFoundError):
            await delete_organization.aexecute(request)
