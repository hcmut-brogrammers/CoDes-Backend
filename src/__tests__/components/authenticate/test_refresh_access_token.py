from datetime import timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from ....common.auth import TokenData
from ....common.models import UserRole
from ....components.authenticate.create_refresh_token import CreateRefreshToken
from ....components.authenticate.refresh_access_token import RefreshAccessToken
from ....components.authenticate.revoke_refresh_token import RevokeRefreshToken
from ....exceptions import BadRequestError
from ....services.jwt_service import ACCESS_TOKEN_EXPIRE_HOURS
from ...utils.common import get_utc_now

MockSetUp = tuple[Mock, Mock, Mock, Mock]


@pytest.fixture
def mocks() -> MockSetUp:
    mock_jwt_service = Mock()
    mock_create_refresh_token = Mock()
    mock_revoke_refresh_token = Mock()
    mock_logger = Mock()
    return mock_jwt_service, mock_create_refresh_token, mock_revoke_refresh_token, mock_logger


class TestRefreshAccessToken:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mocks: MockSetUp) -> None:
        (
            mock_jwt_service,
            mock_create_refresh_token,
            mock_revoke_refresh_token,
            mock_logger,
        ) = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = uuid4()
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = uuid4()

        mock_exp_time = get_utc_now() + timedelta(hours=1)
        token_data = TokenData(
            user_id=uuid4(),
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=uuid4(),
            sub="johndoe",
            exp=int(mock_exp_time.timestamp()),  # Convert datetime to UNIX timestamp
        )
        update_exp = {"exp": int((mock_exp_time + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)).timestamp())}
        extend_exp_token_data = token_data.model_copy(update=update_exp)

        # Mock jwt_service
        mock_jwt_service.configure_mock(
            decode_jwt_token=Mock(return_value=token_data),
            extend_token_data_expiration=Mock(return_value=extend_exp_token_data),
            encode_jwt_token=Mock(return_value=mock_new_access_token),
        )

        # Mock create_refresh_token
        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_new_refresh_token_id))
        )

        # Mock revoke_refresh_token
        mock_revoke_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=RevokeRefreshToken.Response(success=True))
        )

        refresh_access_token = RefreshAccessToken(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            revoke_refresh_token=mock_revoke_refresh_token,
            logger=mock_logger,
        )

        request = RefreshAccessToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)
        response = await refresh_access_token.aexecute(request)

        assert response.access_token == mock_new_access_token
        assert response.refresh_token_id == mock_new_refresh_token_id

        mock_jwt_service.decode_jwt_token.assert_called_once_with(mock_access_token, verify_exp=False)
        mock_revoke_refresh_token.aexecute.assert_called_once_with(
            RevokeRefreshToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)
        )
        mock_jwt_service.extend_token_data_expiration.assert_called_once_with(token_data)
        mock_jwt_service.encode_jwt_token.assert_called_once_with(extend_exp_token_data)
        mock_create_refresh_token.aexecute.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_fail_to_decode_access_token_throw_exception(self, mocks: MockSetUp) -> None:
        (
            mock_jwt_service,
            mock_create_refresh_token,
            mock_revoke_refresh_token,
            mock_logger,
        ) = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = uuid4()
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = uuid4()

        mock_exp_time = get_utc_now() + timedelta(hours=1)
        token_data = TokenData(
            user_id=uuid4(),
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=uuid4(),
            sub="johndoe",
            exp=int(mock_exp_time.timestamp()),  # Convert datetime to UNIX timestamp
        )
        update_exp = {"exp": int((mock_exp_time + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)).timestamp())}
        extend_exp_token_data = token_data.model_copy(update=update_exp)

        # Mock jwt_service
        mock_jwt_service.configure_mock(
            decode_jwt_token=Mock(side_effect=ValueError("Failed to decode access token.")),
            extend_token_data_expiration=Mock(return_value=extend_exp_token_data),
            encode_jwt_token=Mock(return_value=mock_new_access_token),
        )

        # Mock create_refresh_token
        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_new_refresh_token_id))
        )

        # Mock revoke_refresh_token
        mock_revoke_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=RevokeRefreshToken.Response(success=True))
        )

        refresh_access_token = RefreshAccessToken(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            revoke_refresh_token=mock_revoke_refresh_token,
            logger=mock_logger,
        )

        request = RefreshAccessToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)

        with pytest.raises(BadRequestError):
            await refresh_access_token.aexecute(request)

    @pytest.mark.asyncio
    async def test_aexecute_access_token_is_empty_throw_exception(self, mocks: MockSetUp) -> None:
        (
            mock_jwt_service,
            mock_create_refresh_token,
            mock_revoke_refresh_token,
            mock_logger,
        ) = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = uuid4()
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = uuid4()

        mock_exp_time = get_utc_now() + timedelta(hours=1)
        token_data = TokenData(
            user_id=uuid4(),
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=uuid4(),
            sub="johndoe",
            exp=int(mock_exp_time.timestamp()),  # Convert datetime to UNIX timestamp
        )
        update_exp = {"exp": int((mock_exp_time + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)).timestamp())}
        extend_exp_token_data = token_data.model_copy(update=update_exp)

        # Mock jwt_service
        mock_jwt_service.configure_mock(
            decode_jwt_token=Mock(return_value=None),
            extend_token_data_expiration=Mock(return_value=extend_exp_token_data),
            encode_jwt_token=Mock(return_value=mock_new_access_token),
        )

        # Mock create_refresh_token
        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_new_refresh_token_id))
        )

        # Mock revoke_refresh_token
        mock_revoke_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=RevokeRefreshToken.Response(success=True))
        )

        refresh_access_token = RefreshAccessToken(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            revoke_refresh_token=mock_revoke_refresh_token,
            logger=mock_logger,
        )

        request = RefreshAccessToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)

        with pytest.raises(BadRequestError):
            await refresh_access_token.aexecute(request)

        mock_jwt_service.decode_jwt_token.assert_called_once_with(mock_access_token, verify_exp=False)

    @pytest.mark.asyncio
    async def test_aexecute_fail_revoke_refresh_token_throw_exception(self, mocks: MockSetUp) -> None:
        (
            mock_jwt_service,
            mock_create_refresh_token,
            mock_revoke_refresh_token,
            mock_logger,
        ) = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = uuid4()
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = uuid4()

        mock_exp_time = get_utc_now() + timedelta(hours=1)
        token_data = TokenData(
            user_id=uuid4(),
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=uuid4(),
            sub="johndoe",
            exp=int(mock_exp_time.timestamp()),  # Convert datetime to UNIX timestamp
        )
        update_exp = {"exp": int((mock_exp_time + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)).timestamp())}
        extend_exp_token_data = token_data.model_copy(update=update_exp)

        # Mock jwt_service
        mock_jwt_service.configure_mock(
            decode_jwt_token=Mock(return_value=token_data),
            extend_token_data_expiration=Mock(return_value=extend_exp_token_data),
            encode_jwt_token=Mock(return_value=mock_new_access_token),
        )

        # Mock create_refresh_token
        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_new_refresh_token_id))
        )

        # Mock revoke_refresh_token
        mock_revoke_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=RevokeRefreshToken.Response(success=False))
        )

        refresh_access_token = RefreshAccessToken(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            revoke_refresh_token=mock_revoke_refresh_token,
            logger=mock_logger,
        )

        request = RefreshAccessToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)

        with pytest.raises(BadRequestError):
            await refresh_access_token.aexecute(request)

        mock_jwt_service.decode_jwt_token.assert_called_once_with(mock_access_token, verify_exp=False)
        mock_revoke_refresh_token.aexecute.assert_called_once_with(
            RevokeRefreshToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)
        )
