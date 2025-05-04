from unittest.mock import AsyncMock, Mock

import pytest

from ....common.models import JoinOrganizationMember, OrganizationModel, UserRole
from ....components.organizations import CreateOrganization
from ....components.organizations.create_user_default_organization import (
    DEFAULT_AVATAR_URL,
    CreateUserDefaultOrganization,
)
from ....exceptions import BadRequestError
from ....utils.common import generate_uuid


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
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_collection: Mock,
        mock_create_organization: Mock,
        mock_owner_username: str,
        mock_organization: OrganizationModel,
    ) -> None:
        # Arrange
        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=mock_organization.id)),
            find_one=Mock(return_value=None),
        )

        mock_create_organization.configure_mock(
            aexecute=AsyncMock(return_value=CreateOrganization.Response(created_organization=mock_organization))
        )

        create_organization = CreateUserDefaultOrganization(
            db=mock_db, logger=mock_logger, create_organization=mock_create_organization
        )
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

        filter = {
            "owner_id": request.owner_id,
            "is_default": True,
        }
        mock_collection.find_one.assert_called_once_with(filter)

        mock_create_organization.aexecute.assert_called_once_with(
            CreateOrganization.Request(
                name=mock_organization.name,
                avatar_url=mock_organization.avatar_url,
                owner_id=mock_organization.owner_id,
                is_default=True,
                role=UserRole.OrganizationAdmin,
            )
        )

    @pytest.mark.asyncio
    async def test_aexecute_default_organization_exists_throw_exception(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_collection: Mock,
        mock_create_organization: Mock,
        mock_owner_username: str,
        mock_organization: OrganizationModel,
    ) -> None:
        # Arrange
        mock_collection.configure_mock(
            find_one=Mock(return_value=mock_organization.model_dump(by_alias=True)),
        )

        create_organization = CreateUserDefaultOrganization(
            db=mock_db, logger=mock_logger, create_organization=mock_create_organization
        )
        request = CreateUserDefaultOrganization.Request(
            owner_username=mock_owner_username, owner_id=mock_organization.owner_id
        )

        # Act and Assert
        with pytest.raises(BadRequestError):
            await create_organization.aexecute(request)

        filter = {
            "owner_id": request.owner_id,
            "is_default": True,
        }
        mock_collection.find_one.assert_called_once_with(filter)
        mock_create_organization.aexecute.assert_not_called()
