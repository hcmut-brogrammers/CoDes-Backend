from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from ....common.auth import TokenData
from ....common.auth.user_context import UserContext
from ....common.models import UserRole
from ....common.models.organization import OrganizationModel
from ....components.authenticate import RevokeRefreshToken
from ....components.authenticate.create_refresh_token import CreateRefreshToken
from ....components.authenticate.refresh_access_token import RefreshAccessToken
from ....components.organizations.get_organization_by_id import GetOrganizationById
from ....components.switch_organization import SwitchOrganization
from ....exceptions import BadRequestError
from ...utils.common import generate_uuid, get_utc_now

MockSetUp = tuple[Mock, AsyncMock, AsyncMock, Mock, AsyncMock, Mock]


@pytest.fixture
def mocks() -> MockSetUp:
    mock_jwt_service = Mock()
    mock_create_refresh_token = AsyncMock()
    mock_revoke_refresh_token = AsyncMock()
    mock_logger = Mock()
    mock_get_organization_by_id = AsyncMock()
    mock_user_context = Mock()
    return (
        mock_jwt_service,
        mock_create_refresh_token,
        mock_revoke_refresh_token,
        mock_logger,
        mock_get_organization_by_id,
        mock_user_context,
    )


class TestSwitchOrganization:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mocks: MockSetUp) -> None:
        # Arrange
        (
            mock_jwt_service,
            mock_create_refresh_token,
            mock_revoke_refresh_token,
            mock_logger,
            mock_get_organization_by_id,
            mock_user_context,
        ) = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = generate_uuid()
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = generate_uuid()
        mock_current_organization_id = generate_uuid()
        mock_organization_id = generate_uuid()
        mock_user_id = generate_uuid()

        token_data = TokenData(
            user_id=mock_user_id,
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=mock_current_organization_id,
            sub="johndoe",
            exp=int((get_utc_now() + timedelta(hours=1)).timestamp()),
        )

        mock_jwt_service.configure_mock(
            encode_jwt_token=Mock(return_value=mock_new_access_token),
        )

        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_new_refresh_token_id))
        )

        mock_revoke_refresh_token.configure_mock(aexecute=AsyncMock(return_value=Mock(success=True)))

        mock_organization = OrganizationModel(
            _id=mock_current_organization_id,
            name="new organization",
            avatar_url="http://example.com",
            owner_id=mock_user_id,
            is_default=True,
        )
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        mock_user_context.configure_mock(**token_data.model_dump())

        # Act
        switch_organizaition = SwitchOrganization(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            revoke_refresh_token=mock_revoke_refresh_token,
            logger=mock_logger,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
        )
        request = SwitchOrganization.Request(
            access_token=mock_access_token,
            refresh_token_id=mock_refresh_token_id,
            organization_id=mock_organization_id,
        )
        response = await switch_organizaition.aexecute(request)

        # Assert
        assert response.access_token == mock_new_access_token
        assert response.refresh_token_id == mock_new_refresh_token_id

        mock_jwt_service.encode_jwt_token.assert_called_once_with(token_data)
        mock_create_refresh_token.aexecute.assert_called_once_with(
            CreateRefreshToken.Request(access_token=mock_new_access_token)
        )
        mock_revoke_refresh_token.aexecute.assert_called_once_with(
            RevokeRefreshToken.Request(access_token=request.access_token, refresh_token_id=request.refresh_token_id)
        )
        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_organization_id)
        )

    @pytest.mark.asyncio
    async def test_aexecute_same_organization_id_to_switch_throw_exception(self, mocks: MockSetUp) -> None:
        # Arrange
        (
            mock_jwt_service,
            mock_create_refresh_token,
            mock_revoke_refresh_token,
            mock_logger,
            mock_get_organization_by_id,
            mock_user_context,
        ) = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = generate_uuid()
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = generate_uuid()
        mock_current_organization_id = generate_uuid()
        mock_organization_id = generate_uuid()
        mock_user_id = generate_uuid()

        token_data = TokenData(
            user_id=mock_user_id,
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=mock_organization_id,
            sub="johndoe",
            exp=int((get_utc_now() + timedelta(hours=1)).timestamp()),  # Convert datetime to UNIX timestamp
        )

        mock_jwt_service.configure_mock(
            encode_jwt_token=Mock(return_value=mock_new_access_token),
        )

        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_new_refresh_token_id))
        )

        mock_revoke_refresh_token.configure_mock(aexecute=AsyncMock(return_value=Mock(success=True)))

        mock_organization = OrganizationModel(
            name="new organization",
            avatar_url="http://example.com",
            owner_id=mock_user_id,
            is_default=True,
        )
        mock_organization.id = mock_current_organization_id
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        mock_user_context.configure_mock(**token_data.model_dump())

        # Act
        switch_organizaition = SwitchOrganization(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            revoke_refresh_token=mock_revoke_refresh_token,
            logger=mock_logger,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
        )
        request = SwitchOrganization.Request(
            access_token=mock_access_token,
            refresh_token_id=mock_refresh_token_id,
            organization_id=mock_organization_id,
        )

        # Assert
        with pytest.raises(BadRequestError):
            await switch_organizaition.aexecute(request)

    @pytest.mark.asyncio
    async def test_aexecute_organization_not_found(self, mocks: MockSetUp) -> None:
        # Arrange
        (
            mock_jwt_service,
            mock_create_refresh_token,
            mock_revoke_refresh_token,
            mock_logger,
            mock_get_organization_by_id,
            mock_user_context,
        ) = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = generate_uuid()
        mock_organization_id = generate_uuid()
        mock_user_id = generate_uuid()

        token_data = TokenData(
            user_id=mock_user_id,
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=generate_uuid(),
            sub="johndoe",
            exp=int((get_utc_now() + timedelta(hours=1)).timestamp()),
        )

        mock_jwt_service.configure_mock(
            encode_jwt_token=Mock(return_value="new_access_token"),
        )

        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=None))
        )

        mock_user_context.configure_mock(**token_data.model_dump())

        # Act
        switch_organization = SwitchOrganization(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            revoke_refresh_token=mock_revoke_refresh_token,
            logger=mock_logger,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
        )
        request = SwitchOrganization.Request(
            access_token=mock_access_token,
            refresh_token_id=mock_refresh_token_id,
            organization_id=mock_organization_id,
        )

        # Assert
        with pytest.raises(BadRequestError, match=f"Organization with id {mock_organization_id} not found."):
            await switch_organization.aexecute(request)

        mock_get_organization_by_id.aexecute.assert_called_once_with(
            GetOrganizationById.Request(id=mock_organization_id)
        )

    @pytest.mark.asyncio
    async def test_aexecute_fail_to_refresh_access_token_exception(self, mocks: MockSetUp) -> None:
        # Arrange
        (
            mock_jwt_service,
            mock_create_refresh_token,
            mock_revoke_refresh_token,
            mock_logger,
            mock_get_organization_by_id,
            mock_user_context,
        ) = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = generate_uuid()
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = generate_uuid()
        mock_current_organization_id = generate_uuid()
        mock_organization_id = generate_uuid()
        mock_user_id = generate_uuid()

        token_data = TokenData(
            user_id=mock_user_id,
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=mock_current_organization_id,
            sub="johndoe",
            exp=int((get_utc_now() + timedelta(hours=1)).timestamp()),  # Convert datetime to UNIX timestamp
        )

        mock_jwt_service.configure_mock(
            encode_jwt_token=Mock(return_value=mock_new_access_token),
        )

        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_new_refresh_token_id))
        )

        mock_revoke_refresh_token.configure_mock(aexecute=AsyncMock(return_value=Mock(success=False)))

        mock_organization = OrganizationModel(
            name="switch-to organization",
            avatar_url="http://example.com",
            owner_id=mock_user_id,
            is_default=True,
        )
        mock_organization.id = mock_current_organization_id
        mock_get_organization_by_id.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        mock_user_context.configure_mock(**token_data.model_dump())

        # Act
        switch_organizaition = SwitchOrganization(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            revoke_refresh_token=mock_revoke_refresh_token,
            logger=mock_logger,
            get_organization_by_id=mock_get_organization_by_id,
            user_context=mock_user_context,
        )
        request = SwitchOrganization.Request(
            access_token=mock_access_token,
            refresh_token_id=mock_refresh_token_id,
            organization_id=mock_organization_id,
        )

        # Assert
        with pytest.raises(BadRequestError):
            await switch_organizaition.aexecute(request)

        mock_revoke_refresh_token.aexecute.assert_called_once_with(
            RevokeRefreshToken.Request(access_token=request.access_token, refresh_token_id=request.refresh_token_id)
        )
