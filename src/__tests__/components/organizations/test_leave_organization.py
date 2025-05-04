from datetime import timedelta
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from ....common.auth import UserContext
from ....common.models import JoinOrganizationMember, OrganizationModel, UserRole
from ....components.organizations.get_organization_by_id import GetOrganizationById
from ....components.organizations.leave_organization import LeaveOrganization
from ....components.users.remove_user_from_organization import RemoveUserFromOrganization
from ....utils.common import generate_uuid, get_utc_now


@pytest.fixture
def mock_user_context() -> UserContext:
    return UserContext(
        user_id=generate_uuid(),
        username="test_user",
        organization_id=generate_uuid(),
        role=UserRole.OrganizationMember,
        email="test_user@example.com",
        sub="test_user",
        exp=int((get_utc_now() + timedelta(days=1)).timestamp()),
    )


@pytest.fixture
def mock_organization(mock_user_context: UserContext) -> OrganizationModel:
    return OrganizationModel(
        _id=mock_user_context.organization_id,
        avatar_url="http://example.com/avatar.png",
        owner_id=mock_user_context.user_id,
        is_default=True,
        name="Test Organization",
        members=[
            JoinOrganizationMember(
                member_id=mock_user_context.user_id,
                member_role=UserRole.OrganizationMember,
                joined_at=get_utc_now(),
            ),
        ],
    )


@pytest.fixture
def mock_get_organization_by_id() -> AsyncMock:
    return AsyncMock(spec=GetOrganizationById)


@pytest.fixture
def mock_remove_user_from_organization() -> AsyncMock:
    return AsyncMock(spec=RemoveUserFromOrganization)


class TestLeaveOrganization:
    @pytest.mark.asyncio
    async def test_leave_organization_success(
        self,
        mock_get_organization_by_id: Mock,
        mock_remove_user_from_organization: Mock,
        mock_logger: Mock,
        mock_organization: OrganizationModel,
        mock_user_context: UserContext,
    ):
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )
        mock_remove_user_from_organization.configure_mock(
            aexecute=AsyncMock(return_value=RemoveUserFromOrganization.Response(success=True))
        )

        leave_organization = LeaveOrganization(
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            logger=mock_logger,
            remove_user_from_organization=mock_remove_user_from_organization,
        )
        response = await leave_organization.aexecute()

        assert response.success is True
        mock_get_organization_by_id.aexecute.assert_called_once()
        mock_remove_user_from_organization.aexecute.assert_called_once()

    @pytest.mark.asyncio
    async def test_leave_organization_admin_cannot_leave(
        self,
        mock_get_organization_by_id: Mock,
        mock_remove_user_from_organization: Mock,
        mock_logger: Mock,
        mock_user_context: UserContext,
    ):
        mock_user_context.role = UserRole.OrganizationAdmin

        leave_organization = LeaveOrganization(
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            logger=mock_logger,
            remove_user_from_organization=mock_remove_user_from_organization,
        )
        response = await leave_organization.aexecute()

        assert response.success is False

    @pytest.mark.asyncio
    async def test_leave_organization_not_found(
        self,
        mock_get_organization_by_id: Mock,
        mock_remove_user_from_organization: Mock,
        mock_logger: Mock,
        mock_user_context: UserContext,
    ):
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=None))
        )

        leave_organization = LeaveOrganization(
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            logger=mock_logger,
            remove_user_from_organization=mock_remove_user_from_organization,
        )
        response = await leave_organization.aexecute()

        assert response.success is False
        mock_get_organization_by_id.aexecute.assert_called_once()

    @pytest.mark.asyncio
    async def test_leave_organization_user_not_member(
        self,
        mock_get_organization_by_id: Mock,
        mock_remove_user_from_organization: Mock,
        mock_logger: Mock,
        mock_organization: OrganizationModel,
        mock_user_context: UserContext,
    ):
        mock_organization.members = []  # User is not a member
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        leave_organization = LeaveOrganization(
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            logger=mock_logger,
            remove_user_from_organization=mock_remove_user_from_organization,
        )
        response = await leave_organization.aexecute()

        assert response.success is False
        mock_get_organization_by_id.aexecute.assert_called_once()

    @pytest.mark.asyncio
    async def test_leave_organization_remove_user_fails(
        self,
        mock_get_organization_by_id: Mock,
        mock_remove_user_from_organization: Mock,
        mock_logger: Mock,
        mock_organization: OrganizationModel,
        mock_user_context: UserContext,
    ):
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )
        mock_remove_user_from_organization.aexecute.configure_mock(return_value=None)

        leave_organization = LeaveOrganization(
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            logger=mock_logger,
            remove_user_from_organization=mock_remove_user_from_organization,
        )
        response = await leave_organization.aexecute()

        assert response.success is False
        mock_get_organization_by_id.aexecute.assert_called_once()
        mock_remove_user_from_organization.aexecute.assert_called_once()
