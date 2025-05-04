from unittest.mock import AsyncMock, Mock

import pytest

from ....common.models import JoinedOrganization, JoinOrganizationMember, OrganizationModel, UserModel, UserRole
from ....components.organizations import GetOrganizationById, GetOrganizationMembers
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


class TestGetOrganizationMembers:
    @pytest.mark.asyncio
    async def test_aexecute_success(
        self,
        mock_db: Mock,
        mock_collection: Mock,
        mock_logger: Mock,
        mock_get_user_by_id: Mock,
        mock_get_organization_by_id: Mock,
        mock_organization: OrganizationModel,
        mock_users: list[UserModel],
    ) -> None:
        # Arrange
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )
        mock_db.configure_mock(
            get_collection=Mock(return_value=mock_collection),
        )
        mock_users_data = [mock_user.model_dump(by_alias=True) for mock_user in mock_users]
        mock_collection.configure_mock(
            find=Mock(return_value=mock_users_data),
        )

        get_organization_members = GetOrganizationMembers(
            db=mock_db,
            logger=mock_logger,
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
        )
        request = GetOrganizationMembers.Request(organization_id=mock_organization.id)

        # Act
        response = await get_organization_members.aexecute(request)

        # Assert
        assert len(response.members) == len(mock_users)
        for i, member in enumerate(response.members):
            assert member.member_id == mock_users[i].id
            assert member.username == mock_users[i].username
            assert member.email == mock_users[i].email
            assert member.role == mock_organization.members[i].member_role
            assert member.joined_at == mock_organization.members[i].joined_at

        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_organization.id)
        )
        mock_collection.find.assert_called_once_with({"_id": {"$in": [user.id for user in mock_users]}})

    @pytest.mark.asyncio
    async def test_aexecute_when_organization_not_found_should_return_empty(
        self,
        mock_db: Mock,
        mock_collection: Mock,
        mock_logger: Mock,
        mock_get_user_by_id: Mock,
        mock_get_organization_by_id: Mock,
    ) -> None:
        # Arrange
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=None))
        )
        get_organization_members = GetOrganizationMembers(
            db=mock_db,
            logger=mock_logger,
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
        )
        request = GetOrganizationMembers.Request(organization_id=generate_uuid())

        # Act
        response = await get_organization_members.aexecute(request)

        # Assert
        assert response.members == []
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=request.organization_id)
        )
        mock_collection.find.assert_not_called()

    @pytest.mark.asyncio
    async def test_aexecute_when_no_members_found_should_return_empty(
        self,
        mock_db: Mock,
        mock_collection: Mock,
        mock_logger: Mock,
        mock_get_user_by_id: Mock,
        mock_get_organization_by_id: Mock,
        mock_organization: OrganizationModel,
    ) -> None:
        # Arrange
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )
        mock_db.configure_mock(
            get_collection=Mock(return_value=mock_collection),
        )
        mock_collection.configure_mock(
            find=Mock(return_value=[]),
        )

        get_organization_members = GetOrganizationMembers(
            db=mock_db,
            logger=mock_logger,
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
        )
        request = GetOrganizationMembers.Request(organization_id=mock_organization.id)

        # Act
        response = await get_organization_members.aexecute(request)

        # Assert
        assert response.members == []
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_organization.id)
        )
        mock_collection.find.assert_called_once_with(
            {"_id": {"$in": [member.member_id for member in mock_organization.members]}}
        )

    @pytest.mark.asyncio
    async def test_aexecute_when_member_not_in_organization(
        self,
        mock_db: Mock,
        mock_collection: Mock,
        mock_logger: Mock,
        mock_get_user_by_id: Mock,
        mock_get_organization_by_id: Mock,
        mock_organization: OrganizationModel,
        mock_users: list[UserModel],
    ) -> None:
        # Arrange

        mock_users[0].id = generate_uuid()  # Change the ID to one not in the organization
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )
        mock_db.configure_mock(
            get_collection=Mock(return_value=mock_collection),
        )
        mock_users_data = [mock_user.model_dump(by_alias=True) for mock_user in mock_users]
        mock_collection.configure_mock(
            find=Mock(return_value=mock_users_data),
        )

        get_organization_members = GetOrganizationMembers(
            db=mock_db,
            logger=mock_logger,
            get_user_by_id=mock_get_user_by_id,
            get_organization_by_id=mock_get_organization_by_id,
        )
        request = GetOrganizationMembers.Request(organization_id=mock_organization.id)

        # Act
        response = await get_organization_members.aexecute(request)

        # Assert
        assert len(response.members) == len(mock_users) - 1  # One user is excluded
        for member in response.members:
            assert member.member_id != mock_users[0].id  # Ensure the excluded user is not in the response

        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_organization.id)
        )
        mock_collection.find.assert_called_once_with(
            {"_id": {"$in": [member.member_id for member in mock_organization.members]}}
        )
