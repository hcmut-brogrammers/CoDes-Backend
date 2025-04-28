from unittest.mock import AsyncMock, Mock, call
from uuid import UUID, uuid4

import pytest

from ....common.models import OrganizationModel
from ....components.organizations.create_default_organization import (
    DEFAULT_AVATAR_URL,
    CreateDefaultOrganization,
    gen_default_organization_name,
)
from ....exceptions import BadRequestError, InternalServerError

MockSetUp = tuple[Mock, Mock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_collection


class TestCreateDefaultOrganization:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        # Mock
        mock_owner_id = UUID("b04b2b91-3d1f-49e3-b5e6-4cb41c7dcdaf")
        mock_owner_name = "owner name sample"

        default_organization_name = gen_default_organization_name(mock_owner_name)

        # Mock request and database response
        organization = OrganizationModel(
            name=default_organization_name,
            avatar_url=DEFAULT_AVATAR_URL,
            owner_id=mock_owner_id,
            is_default=True,
        )
        first_result = None
        second_result = organization.model_dump(by_alias=True)
        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=organization.id)),
            find_one=Mock(side_effect=[first_result, second_result]),
        )

        # Initialize the component
        create_organization = CreateDefaultOrganization(db=mock_db, logger=mock_logger)

        # Execute the component
        request = CreateDefaultOrganization.Request(owner_name=mock_owner_name, owner_id=organization.owner_id)
        response = await create_organization.aexecute(request)

        # Assertions
        assert response.created_organization is not None
        assert response.created_organization.owner_id == organization.owner_id
        assert response.created_organization.name == organization.name
        assert response.created_organization.avatar_url == organization.avatar_url
        assert response.created_organization.is_default == organization.is_default

        # Verify interactions
        mock_collection.insert_one.assert_called_once()
        filter = {
            "owner_id": request.owner_id,
            "is_default": True,
        }
        mock_collection.find_one.call_count == 2
        expect_calls = [call(filter), call({"_id": organization.id})]
        assert mock_collection.find_one.call_args_list == expect_calls

    @pytest.mark.asyncio
    async def test_aexecute_default_organization_exists_throw_exception(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        # Mock
        mock_owner_id = UUID("b04b2b91-3d1f-49e3-b5e6-4cb41c7dcdaf")
        mock_owner_name = "owner name sample"

        default_organization_name = gen_default_organization_name(mock_owner_name)

        # Mock request and database response
        organization = OrganizationModel(
            name=default_organization_name,
            avatar_url=DEFAULT_AVATAR_URL,
            owner_id=mock_owner_id,
            is_default=True,
        )
        first_result = organization.model_dump(by_alias=True)
        second_result = None
        mock_collection.configure_mock(
            find_one=Mock(side_effect=[first_result, second_result]),
        )

        # Initialize the component
        create_organization = CreateDefaultOrganization(db=mock_db, logger=mock_logger)

        # Execute the component with expected Error
        request = CreateDefaultOrganization.Request(owner_name=mock_owner_name, owner_id=organization.owner_id)

        with pytest.raises(BadRequestError):
            await create_organization.aexecute(request)

        # Verify interactions
        mock_collection.find_one.call_count == 1
        filter = {
            "owner_id": request.owner_id,
            "is_default": True,
        }
        expect_calls = [call(filter)]
        assert mock_collection.find_one.call_args_list == expect_calls

    @pytest.mark.asyncio
    async def test_aexecute_success_insert_but_fail_retrieve(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        # Mock
        mock_owner_id = UUID("b04b2b91-3d1f-49e3-b5e6-4cb41c7dcdaf")
        mock_wrong_returned_organization_inserted_id = UUID("b3de8d61-9b1c-4bb1-8f98-72a613d6230a")
        mock_owner_name = "owner name sample"

        default_organization_name = gen_default_organization_name(mock_owner_name)

        # Mock request and database response
        organization = OrganizationModel(
            name=default_organization_name,
            avatar_url=DEFAULT_AVATAR_URL,
            owner_id=mock_owner_id,
            is_default=True,
        )
        first_result = None
        second_result = None
        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=mock_wrong_returned_organization_inserted_id)),
            find_one=Mock(side_effect=[first_result, second_result]),
        )

        # Initialize the component
        create_organization = CreateDefaultOrganization(db=mock_db, logger=mock_logger)

        # Execute the component
        request = CreateDefaultOrganization.Request(owner_name=mock_owner_name, owner_id=organization.owner_id)
        with pytest.raises(InternalServerError):
            await create_organization.aexecute(request)

        # Verify interactions
        mock_collection.insert_one.assert_called_once()
        filter = {
            "owner_id": request.owner_id,
            "is_default": True,
        }
        mock_collection.find_one.call_count == 2
        expect_calls = [call(filter), call({"_id": mock_wrong_returned_organization_inserted_id})]
        assert mock_collection.find_one.call_args_list == expect_calls
