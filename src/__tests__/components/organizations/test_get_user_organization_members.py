from unittest.mock import AsyncMock, Mock

import pytest

from ....common.models import JoinedOrganization, JoinOrganizationMember, OrganizationModel, UserModel, UserRole
from ....components.organizations import GetOrganizationMembers, GetUserOrganizationMembers
from ....utils.common import generate_uuid, get_utc_now


@pytest.fixture
def mock_organization() -> OrganizationModel:
    return OrganizationModel(
        name="Test Organization",
        owner_id=generate_uuid(),
        is_default=False,
        members=[
            JoinOrganizationMember(
                member_id=generate_uuid(),
                member_role=UserRole.OrganizationAdmin,
                joined_at=get_utc_now(),
            ),
            JoinOrganizationMember(
                member_id=generate_uuid(),
                member_role=UserRole.OrganizationMember,
                joined_at=get_utc_now(),
            ),
        ],
    )


@pytest.fixture
def mock_users(mock_organization: OrganizationModel) -> list[UserModel]:
    return [
        UserModel(
            _id=mock_organization.members[0].member_id,
            username="admin_user",
            email="admin@example.com",
            hashed_password="hashed_password",
            role=UserRole.OrganizationAdmin,
            joined_organizations=[
                JoinedOrganization(
                    organization_id=mock_organization.id,
                    role=mock_organization.members[0].member_role,
                    joined_at=mock_organization.members[0].joined_at,
                )
            ],
        ),
        UserModel(
            _id=mock_organization.members[1].member_id,
            username="member_user",
            email="member@example.com",
            hashed_password="hashed_password",
            role=UserRole.OrganizationMember,
            joined_organizations=[
                JoinedOrganization(
                    organization_id=mock_organization.id,
                    role=mock_organization.members[1].member_role,
                    joined_at=mock_organization.members[1].joined_at,
                )
            ],
        ),
    ]


@pytest.fixture
def mock_members(mock_users: list[UserModel]) -> list[GetOrganizationMembers.Member]:
    return [
        GetOrganizationMembers.Member(
            member_id=mock_user.id,
            username=mock_user.username,
            email=mock_user.email,
            role=mock_user.role,
            joined_at=mock_user.joined_organizations[0].joined_at,
        )
        for mock_user in mock_users
    ]


# Fixture for mock GetOrganizationMembers
@pytest.fixture
def mock_get_organization_members() -> Mock:
    return Mock(spec=GetOrganizationMembers)


class TestGetUserOrganizationMembers:
    @pytest.mark.asyncio
    async def test_aexecute_success(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_user_context: Mock,
        mock_get_organization_members: Mock,
        mock_organization: Mock,
        mock_members: list[GetOrganizationMembers.Member],
    ) -> None:
        # Arrange
        mock_user_context.configure_mock(organization_id=mock_organization.id)
        mock_get_organization_members.configure_mock(
            aexecute=AsyncMock(return_value=GetUserOrganizationMembers.Response(members=mock_members))
        )

        get_user_organization_members = GetUserOrganizationMembers(
            db=mock_db,
            logger=mock_logger,
            user_context=mock_user_context,
            get_organization_members=mock_get_organization_members,
        )

        # Act
        response = await get_user_organization_members.aexecute()

        # Assert
        assert len(response.members) == len(mock_members)
        for i, member in enumerate(response.members):
            assert member.member_id == mock_members[i].member_id
            assert member.username == mock_members[i].username
            assert member.email == mock_members[i].email
            assert member.role == mock_members[i].role
            assert member.joined_at == mock_members[i].joined_at

        mock_get_organization_members.aexecute.assert_called_once()
