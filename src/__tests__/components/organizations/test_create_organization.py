from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from ....common.models import JoinOrganizationMember, OrganizationModel, UserRole
from ....components.organizations import CreateOrganization
from ....exceptions import InternalServerError
from ....utils.common import generate_uuid


@pytest.fixture
def mock_owner_id() -> UUID:
    return generate_uuid()


@pytest.fixture
def mock_organization(mock_owner_id: UUID) -> OrganizationModel:
    return OrganizationModel(
        name="Test Organization",
        avatar_url="http://example.com/avatar.png",
        owner_id=mock_owner_id,
        is_default=False,
        members=[
            JoinOrganizationMember(
                member_id=mock_owner_id,
                member_role=UserRole.OrganizationAdmin,
            )
        ],
    )


class TestCreateOrganization:
    @pytest.mark.asyncio
    async def test_aexecute_success(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_collection: Mock,
        mock_add_user_to_organization: Mock,
        mock_owner_id: UUID,
        mock_organization: OrganizationModel,
    ) -> None:
        # Arrange
        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=mock_organization.id)),
            find_one=Mock(return_value=mock_organization.model_dump(by_alias=True)),
        )

        mock_add_user_to_organization.configure_mock(
            aexecute=AsyncMock(return_value=Mock(join_organization_member=mock_organization.members[0]))
        )

        create_organization = CreateOrganization(
            db=mock_db, logger=mock_logger, add_user_to_organization=mock_add_user_to_organization
        )
        request = CreateOrganization.Request(
            name=mock_organization.name,
            avatar_url=mock_organization.avatar_url,
            owner_id=mock_owner_id,
            is_default=False,
            role=UserRole.OrganizationAdmin,
        )

        # Act
        response = await create_organization.aexecute(request)

        # Assert
        assert response.created_organization is not None
        assert response.created_organization.name == mock_organization.name
        assert response.created_organization.owner_id == mock_owner_id
        assert response.created_organization.avatar_url == mock_organization.avatar_url
        assert response.created_organization.is_default == mock_organization.is_default
        assert len(response.created_organization.members) == 1

        mock_collection.insert_one.assert_called_once()
        mock_collection.find_one.assert_called_once_with({"_id": mock_organization.id})
        mock_add_user_to_organization.aexecute.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_when_organization_inserted_but_not_found_should_throw_internal_server_error(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_collection: Mock,
        mock_add_user_to_organization: Mock,
        mock_owner_id: UUID,
        mock_organization: OrganizationModel,
    ) -> None:
        # Arrange
        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=mock_organization.id)),
            find_one=Mock(return_value=None),
        )

        create_organization = CreateOrganization(
            db=mock_db, logger=mock_logger, add_user_to_organization=mock_add_user_to_organization
        )
        request = CreateOrganization.Request(
            name=mock_organization.name,
            avatar_url=mock_organization.avatar_url,
            owner_id=mock_owner_id,
            is_default=False,
            role=UserRole.OrganizationAdmin,
        )

        # Act and Assert
        with pytest.raises(InternalServerError):
            await create_organization.aexecute(request)

        mock_collection.insert_one.assert_called_once()
        mock_collection.find_one.assert_called_once_with({"_id": mock_organization.id})
        mock_add_user_to_organization.aexecute.assert_not_called()

    @pytest.mark.asyncio
    async def test_aexecute_when_add_user_to_organization_failed_should_throw_internal_server_error(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_collection: Mock,
        mock_add_user_to_organization: Mock,
        mock_owner_id: UUID,
        mock_organization: OrganizationModel,
    ) -> None:
        # Arrange
        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=mock_organization.id)),
            find_one=Mock(return_value=mock_organization.model_dump(by_alias=True)),
        )

        mock_add_user_to_organization.configure_mock(aexecute=AsyncMock(return_value=None))

        create_organization = CreateOrganization(
            db=mock_db, logger=mock_logger, add_user_to_organization=mock_add_user_to_organization
        )
        request = CreateOrganization.Request(
            name=mock_organization.name,
            avatar_url=mock_organization.avatar_url,
            owner_id=mock_owner_id,
            is_default=False,
            role=UserRole.OrganizationAdmin,
        )

        # Act and Assert
        with pytest.raises(InternalServerError):
            await create_organization.aexecute(request)

        mock_collection.insert_one.assert_called_once()
        mock_collection.find_one.assert_called_once_with({"_id": mock_organization.id})
        mock_add_user_to_organization.aexecute.assert_called_once()
