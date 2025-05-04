from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from ....common.models import JoinOrganizationMember, OrganizationModel, UserRole
from ....components.organizations import CreateOrganization, CreateUserOrganization
from ....utils.common import generate_uuid, get_utc_now


@pytest.fixture
def mock_owner_id() -> UUID:
    return generate_uuid()


@pytest.fixture
def mock_default_organization(mock_owner_id: UUID) -> OrganizationModel:
    return OrganizationModel(
        name="org_test",
        avatar_url="http://example.com/avatar.png",
        owner_id=mock_owner_id,
        is_default=True,
        members=[
            JoinOrganizationMember(
                member_id=mock_owner_id,
                member_role=UserRole.OrganizationAdmin,
                joined_at=get_utc_now(),
            )
        ],
    )


@pytest.fixture
def mock_non_default_organization(mock_default_organization: OrganizationModel) -> OrganizationModel:
    organization = mock_default_organization.model_copy()
    organization.is_default = False
    return organization


class TestCreateOrganization:
    @pytest.mark.asyncio
    async def test_aexecute_success(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_collection: Mock,
        mock_user_context: Mock,
        mock_create_organization: Mock,
        mock_owner_id: UUID,
        mock_default_organization: OrganizationModel,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_owner_id)
        mock_collection.configure_mock(
            find_one=Mock(return_value=None),
        )

        mock_create_organization.configure_mock(
            aexecute=AsyncMock(
                return_value=CreateOrganization.Response(created_organization=mock_default_organization)
            ),
        )

        create_organization = CreateUserOrganization(
            db=mock_db, logger=mock_logger, create_organization=mock_create_organization, user_context=mock_user_context
        )
        request = CreateUserOrganization.Request(
            name=mock_default_organization.name, avatar_url=mock_default_organization.avatar_url
        )

        # Act
        response = await create_organization.aexecute(request)

        # Assert
        assert response.created_organization is not None
        assert response.created_organization.owner_id == mock_owner_id
        assert response.created_organization.name == mock_default_organization.name
        assert response.created_organization.avatar_url == mock_default_organization.avatar_url
        assert response.created_organization.is_default is True
        assert len(response.created_organization.members) == 1

        filter = {
            "owner_id": mock_owner_id,
            "is_default": True,
        }
        mock_collection.find_one.assert_called_once_with(filter)

        mock_create_organization.aexecute.assert_called_once_with(
            CreateOrganization.Request(
                name=mock_default_organization.name,
                avatar_url=mock_default_organization.avatar_url,
                owner_id=mock_owner_id,
                is_default=True,
                role=UserRole.OrganizationAdmin,
            )
        )

    @pytest.mark.asyncio
    async def test_aexecute_default_organization_exists_success(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_collection: Mock,
        mock_user_context: Mock,
        mock_create_organization: Mock,
        mock_owner_id: UUID,
        mock_default_organization: OrganizationModel,
        mock_non_default_organization: OrganizationModel,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_owner_id)
        mock_collection.configure_mock(
            find_one=Mock(return_value=mock_default_organization.model_dump(by_alias=True)),
        )

        mock_create_organization.configure_mock(
            aexecute=AsyncMock(
                return_value=CreateOrganization.Response(created_organization=mock_non_default_organization)
            ),
        )

        create_organization = CreateUserOrganization(
            db=mock_db, logger=mock_logger, create_organization=mock_create_organization, user_context=mock_user_context
        )
        request = CreateUserOrganization.Request(
            name=mock_non_default_organization.name, avatar_url=mock_non_default_organization.avatar_url
        )

        # Act
        response = await create_organization.aexecute(request)

        # Assert
        assert response.created_organization is not None
        assert response.created_organization.owner_id == mock_non_default_organization.owner_id
        assert response.created_organization.name == mock_non_default_organization.name
        assert response.created_organization.avatar_url == mock_non_default_organization.avatar_url
        assert response.created_organization.is_default is False
        assert len(response.created_organization.members) == 1

        filter = {
            "owner_id": mock_owner_id,
            "is_default": True,
        }
        mock_collection.find_one.assert_called_once_with(filter)

        mock_create_organization.aexecute.assert_called_once_with(
            CreateOrganization.Request(
                name=mock_non_default_organization.name,
                avatar_url=mock_non_default_organization.avatar_url,
                owner_id=mock_owner_id,
                is_default=False,
                role=UserRole.OrganizationAdmin,
            )
        )
