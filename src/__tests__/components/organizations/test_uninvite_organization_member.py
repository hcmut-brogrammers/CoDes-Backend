from datetime import timedelta
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from ....common.auth import UserContext
from ....common.models import JoinOrganizationMember, OrganizationModel, UserRole
from ....components.organizations.get_organization_by_id import GetOrganizationById
from ....components.organizations.uninvite_organization_member import UninviteOrganzationMember
from ....components.users.remove_user_from_organization import RemoveUserFromOrganization
from ....utils.common import generate_uuid, get_utc_now


@pytest.fixture
def mock_user_context() -> UserContext:
    user_context = UserContext(
        user_id=generate_uuid(),
        username="username",
        organization_id=generate_uuid(),
        role=UserRole.OrganizationAdmin,
        email="user@gmail.com",
        sub="username",
        exp=int((get_utc_now() + timedelta(days=1)).timestamp()),
    )
    return user_context


@pytest.fixture
def mock_member_id() -> UUID:
    return generate_uuid()


@pytest.fixture
def mock_organization(mock_user_context: UserContext, mock_member_id: UUID) -> OrganizationModel:
    return OrganizationModel(
        _id=mock_user_context.organization_id,
        name="Test Organization",
        avatar_url="http://example.com/avatar.png",
        owner_id=mock_user_context.user_id,
        is_default=False,
        members=[
            JoinOrganizationMember(
                member_id=mock_user_context.user_id,
                member_role=UserRole.OrganizationAdmin,
            ),
            JoinOrganizationMember(
                member_id=mock_member_id,
                member_role=UserRole.OrganizationMember,
            ),
        ],
    )


class TestUninviteOrganzationMember:
    @pytest.mark.asyncio
    async def test_aexecute_when_user_is_not_admin_should_return_failure(
        self,
        mock_user_context: UserContext,
        mock_logger: Mock,
        mock_get_organization_by_id: Mock,
        mock_remove_user_from_organization: Mock,
    ) -> None:
        # Arrange
        mock_user_context.role = UserRole.OrganizationMember

        uninvite_member = UninviteOrganzationMember(
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            logger=mock_logger,
            remove_user_from_organization=mock_remove_user_from_organization,
        )

        request = UninviteOrganzationMember.Request(member_id=generate_uuid())

        # Act
        response = await uninvite_member.aexecute(request)

        # Assert
        assert response.success is False

    @pytest.mark.asyncio
    async def test_aexecute_when_organization_not_found_should_return_failure(
        self,
        mock_user_context: UserContext,
        mock_logger: Mock,
        mock_get_organization_by_id: Mock,
        mock_remove_user_from_organization: Mock,
    ) -> None:
        # Arrange
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=None))
        )

        uninvite_member = UninviteOrganzationMember(
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            logger=mock_logger,
            remove_user_from_organization=mock_remove_user_from_organization,
        )

        request = UninviteOrganzationMember.Request(member_id=generate_uuid())

        # Act
        response = await uninvite_member.aexecute(request)

        # Assert
        assert response.success is False
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_user_context.organization_id)
        )

    @pytest.mark.asyncio
    async def test_aexecute_when_member_not_in_organization_should_return_failure(
        self,
        mock_user_context: UserContext,
        mock_logger: Mock,
        mock_get_organization_by_id: Mock,
        mock_remove_user_from_organization: Mock,
        mock_organization: OrganizationModel,
    ) -> None:
        # Arrange
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        uninvite_member = UninviteOrganzationMember(
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            logger=mock_logger,
            remove_user_from_organization=mock_remove_user_from_organization,
        )
        mock_uninvited_member_id = generate_uuid()
        request = UninviteOrganzationMember.Request(member_id=mock_uninvited_member_id)

        # Act
        response = await uninvite_member.aexecute(request)

        # Assert
        assert response.success is False
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_user_context.organization_id)
        )

    @pytest.mark.asyncio
    async def test_aexecute_when_remove_user_fails_should_return_failure(
        self,
        mock_user_context: UserContext,
        mock_logger: Mock,
        mock_get_organization_by_id: Mock,
        mock_remove_user_from_organization: Mock,
        mock_organization: OrganizationModel,
        mock_member_id: UUID,
    ) -> None:
        # Arrange
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        mock_remove_user_from_organization.configure_mock(aexecute=AsyncMock(return_value=None))

        uninvite_member = UninviteOrganzationMember(
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            logger=mock_logger,
            remove_user_from_organization=mock_remove_user_from_organization,
        )

        request = UninviteOrganzationMember.Request(member_id=mock_member_id)

        # Act
        response = await uninvite_member.aexecute(request)

        # Assert
        assert response.success is False
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_user_context.organization_id)
        )
        mock_remove_user_from_organization.aexecute.assert_called_once_with(
            RemoveUserFromOrganization.Request(
                organization_id=mock_user_context.organization_id,
                user_id=request.member_id,
            )
        )

    @pytest.mark.asyncio
    async def test_aexecute_when_successful_should_return_success(
        self,
        mock_user_context: UserContext,
        mock_logger: Mock,
        mock_get_organization_by_id: Mock,
        mock_remove_user_from_organization: Mock,
        mock_organization: OrganizationModel,
        mock_member_id: UUID,
    ) -> None:
        # Arrange
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        mock_remove_user_from_organization.configure_mock(
            aexecute=AsyncMock(return_value=RemoveUserFromOrganization.Response(success=True))
        )

        uninvite_member = UninviteOrganzationMember(
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
            logger=mock_logger,
            remove_user_from_organization=mock_remove_user_from_organization,
        )

        request = UninviteOrganzationMember.Request(member_id=mock_member_id)

        # Act
        response = await uninvite_member.aexecute(request)

        # Assert
        assert response.success is True
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_user_context.organization_id)
        )
        mock_remove_user_from_organization.aexecute.assert_called_once_with(
            RemoveUserFromOrganization.Request(
                organization_id=mock_user_context.organization_id,
                user_id=request.member_id,
            )
        )
