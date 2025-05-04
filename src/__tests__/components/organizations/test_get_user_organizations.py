from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from ....common.models import JoinedOrganization, JoinOrganizationMember, OrganizationModel, UserModel, UserRole
from ....components.organizations.get_user_organizations import GetUserById, GetUserOrganizations
from ....exceptions import NotFoundError
from ....utils.common import generate_uuid, get_utc_now

MockSetUp = tuple[Mock, Mock, Mock, AsyncMock]


@pytest.fixture
def mock_user_id() -> UUID:
    return generate_uuid()


@pytest.fixture
def mock_user(mock_user_id: UUID) -> UserModel:
    return UserModel(
        _id=mock_user_id,
        email="user@gmail.com",
        hashed_password="hashed_password",
        role=UserRole.OrganizationAdmin,
        username="username",
        joined_organizations=[
            JoinedOrganization(
                organization_id=generate_uuid(),
                role=UserRole.OrganizationAdmin,
                joined_at=get_utc_now(),
            )
        ],
    )


@pytest.fixture
def mock_organization(mock_user_id: UUID) -> OrganizationModel:
    return OrganizationModel(
        _id=generate_uuid(),
        avatar_url="http://example.com/avatar.png",
        name="organization name",
        owner_id=mock_user_id,
        members=[
            JoinOrganizationMember(
                member_id=mock_user_id,
                member_role=UserRole.OrganizationAdmin,
                joined_at=get_utc_now(),
            )
        ],
    )


class TestGetOrganizationByOwnerId:
    @pytest.mark.asyncio
    async def test_aexecute_success(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_collection: Mock,
        mock_get_user_by_id: Mock,
        mock_user_id: UUID,
        mock_user: UserModel,
        mock_organization: OrganizationModel,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_user_id)
        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=GetUserById.Response(user=mock_user)))

        mock_organizations = [mock_organization]
        mock_organizations_data = [
            mock_organization.model_dump(by_alias=True) for mock_organization in mock_organizations
        ]
        mock_collection.configure_mock(find=Mock(return_value=mock_organizations_data))

        get_organization_by_id = GetUserOrganizations(
            db=mock_db, logger=mock_logger, user_context=mock_user_context, get_user_by_id=mock_get_user_by_id
        )

        # Act
        response = await get_organization_by_id.aexecute()

        # Assertions
        assert len(response.organizations) == len(mock_organizations)
        for organization, mock_organization in zip(response.organizations, mock_organizations):
            assert organization.name == mock_organization.name
            assert organization.avatar_url == mock_organization.avatar_url
            assert organization.owner_id == mock_user_id
            assert organization.is_default == mock_organization.is_default
            assert len(organization.members) == len(mock_organization.members)
            for member, mock_member in zip(organization.members, mock_organization.members):
                assert member.member_id == mock_member.member_id
                assert member.member_role == mock_member.member_role
                assert member.joined_at == mock_member.joined_at

        # Verify interactions
        mock_get_user_by_id.aexecute.assert_called_once_with(GetUserById.Request(user_id=mock_user_id))
        mock_collection.find.assert_called_once_with(
            {
                "_id": {
                    "$in": [mock_organization.organization_id for mock_organization in mock_user.joined_organizations]
                }
            }
        )

    @pytest.mark.asyncio
    async def test_aexecute_when_user_not_found_should_throw_not_found_error(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_collection: Mock,
        mock_get_user_by_id: Mock,
        mock_user_id: UUID,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_user_id)
        mock_collection.configure_mock(find=Mock(return_value=None))
        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=GetUserById.Response(user=None)))

        get_organization_by_id = GetUserOrganizations(
            db=mock_db, logger=mock_logger, user_context=mock_user_context, get_user_by_id=mock_get_user_by_id
        )

        # Act and Assert
        with pytest.raises(NotFoundError):
            await get_organization_by_id.aexecute()
        mock_get_user_by_id.aexecute.assert_called_once_with(GetUserById.Request(user_id=mock_user_id))

    @pytest.mark.asyncio
    async def test_aexecute_when_organization_not_found_should_throw_not_found_error(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_collection: Mock,
        mock_get_user_by_id: Mock,
        mock_user_id: UUID,
        mock_user: UserModel,
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(user_id=mock_user_id)
        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=GetUserById.Response(user=mock_user)))

        mock_collection.configure_mock(find=Mock(return_value=None))

        get_organization_by_id = GetUserOrganizations(
            db=mock_db, logger=mock_logger, user_context=mock_user_context, get_user_by_id=mock_get_user_by_id
        )

        # Act and Assert
        with pytest.raises(NotFoundError):
            await get_organization_by_id.aexecute()

        mock_get_user_by_id.aexecute.assert_called_once_with(GetUserById.Request(user_id=mock_user_id))
        mock_collection.find.assert_called_once_with(
            {
                "_id": {
                    "$in": [mock_organization.organization_id for mock_organization in mock_user.joined_organizations]
                }
            }
        )
