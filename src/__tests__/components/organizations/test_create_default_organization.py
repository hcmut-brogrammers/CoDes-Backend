from unittest.mock import AsyncMock, Mock, call
from uuid import UUID

import pytest

from ....common.models import JoinOrganizationMember, OrganizationModel, UserRole
from ....components.organizations.create_user_default_organization import (
    DEFAULT_AVATAR_URL,
    CreateUserDefaultOrganization,
)
from ....exceptions import BadRequestError, InternalServerError
from ....utils.common import generate_uuid

MockSetUp = tuple[Mock, Mock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_collection


@pytest.fixture
def mock_owner_username() -> str:
    return "username"


@pytest.fixture
def mock_organization(mock_owner_username: str) -> OrganizationModel:
    owner_id = generate_uuid()
    organization_name = f"{mock_owner_username[0].upper()}{mock_owner_username[1:]}'s Default Organization"
    return OrganizationModel(
        name=organization_name,
        avatar_url=DEFAULT_AVATAR_URL,
        owner_id=owner_id,
        is_default=True,
        members=[JoinOrganizationMember(member_id=owner_id, member_role=UserRole.OrganizationAdmin)],
    )


class TestCreateDefaultOrganization:
    @pytest.mark.asyncio
    async def test_aexecute_success(
        self, mock_setup: MockSetUp, mock_owner_username: str, mock_organization: OrganizationModel
    ) -> None:
        # Arrange
        mock_db, mock_logger, mock_collection = mock_setup

        first_result = None
        second_result = mock_organization.model_dump(by_alias=True)
        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=mock_organization.id)),
            find_one=Mock(side_effect=[first_result, second_result]),
        )

        create_organization = CreateUserDefaultOrganization(db=mock_db, logger=mock_logger)
        request = CreateUserDefaultOrganization.Request(
            owner_username=mock_owner_username, owner_id=mock_organization.owner_id
        )

        # Act
        response = await create_organization.aexecute(request)

        # Assert
        assert response.created_organization is not None
        assert response.created_organization.owner_id == mock_organization.owner_id
        assert response.created_organization.name == mock_organization.name
        assert response.created_organization.avatar_url == mock_organization.avatar_url
        assert response.created_organization.is_default == mock_organization.is_default
        assert len(response.created_organization.members) == 1
        member = response.created_organization.members[0]
        assert member.member_id == mock_organization.owner_id
        assert member.member_role == UserRole.OrganizationAdmin

        mock_collection.insert_one.assert_called_once()
        filter = {
            "owner_id": request.owner_id,
            "is_default": True,
        }
        mock_collection.find_one.call_count == 2
        expect_calls = [call(filter), call({"_id": mock_organization.id})]
        assert mock_collection.find_one.call_args_list == expect_calls

    @pytest.mark.asyncio
    async def test_aexecute_default_organization_exists_throw_exception(
        self, mock_setup: MockSetUp, mock_organization: OrganizationModel, mock_owner_username: str
    ) -> None:
        # Arrange
        mock_db, mock_logger, mock_collection = mock_setup

        first_result = mock_organization.model_dump(by_alias=True)
        second_result = None
        mock_collection.configure_mock(
            find_one=Mock(side_effect=[first_result, second_result]),
        )

        create_organization = CreateUserDefaultOrganization(db=mock_db, logger=mock_logger)
        request = CreateUserDefaultOrganization.Request(
            owner_username=mock_owner_username, owner_id=mock_organization.owner_id
        )

        # Act and Assert
        with pytest.raises(BadRequestError):
            await create_organization.aexecute(request)

        mock_collection.find_one.call_count == 1
        filter = {
            "owner_id": request.owner_id,
            "is_default": True,
        }
        expect_calls = [call(filter)]
        assert mock_collection.find_one.call_args_list == expect_calls

    @pytest.mark.asyncio
    async def test_aexecute_success_insert_but_fail_retrieve(
        self, mock_setup: MockSetUp, mock_organization: OrganizationModel, mock_owner_username: str
    ) -> None:
        # Arrange
        mock_db, mock_logger, mock_collection = mock_setup
        mock_wrong_returned_organization_inserted_id = generate_uuid()

        first_result = None
        second_result = None
        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=mock_wrong_returned_organization_inserted_id)),
            find_one=Mock(side_effect=[first_result, second_result]),
        )

        create_organization = CreateUserDefaultOrganization(db=mock_db, logger=mock_logger)
        request = CreateUserDefaultOrganization.Request(
            owner_username=mock_owner_username, owner_id=mock_organization.owner_id
        )

        # Act and Assert
        with pytest.raises(InternalServerError):
            await create_organization.aexecute(request)

        mock_collection.insert_one.assert_called_once()
        filter = {
            "owner_id": request.owner_id,
            "is_default": True,
        }
        mock_collection.find_one.call_count == 2
        expect_calls = [call(filter), call({"_id": mock_wrong_returned_organization_inserted_id})]
        assert mock_collection.find_one.call_args_list == expect_calls
