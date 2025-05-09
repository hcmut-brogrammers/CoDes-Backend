from datetime import timedelta
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest

from ....common.models.refresh_token import RefreshTokenModel
from ....components.authenticate.refresh_access_token import RefreshAccessToken
from ....components.authenticate.revoke_refresh_token import RevokeRefreshToken
from ....utils.common import get_utc_now

MockSetUp = tuple[Mock, Mock, Mock, Mock]


@pytest.fixture
def mocks() -> MockSetUp:
    mock_jwt_service = Mock()
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = Mock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_jwt_service, mock_db, mock_logger, mock_collection


class TestRevokeRefreshToken:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_db, mock_logger, mock_collection = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = UUID("3f7c4e8b-5e4d-4326-9fd7-bcf8d470cb10")

        refresh_token = RefreshTokenModel(
            hashed_access_token="hashed_access_token",
            expired_at=get_utc_now() + timedelta(days=1),
            revoked_at=None,
        )

        # Mock collection
        mock_collection.configure_mock(find_one=Mock(return_value=refresh_token.model_dump(by_alias=True)))

        # Mock jwt_service
        mock_jwt_service.configure_mock(
            verify_password=Mock(return_value=True),
        )

        # Initialize the component
        revoke_access_token = RevokeRefreshToken(
            db=mock_db,
            jwt_service=mock_jwt_service,
            logger=mock_logger,
        )

        request = RevokeRefreshToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)
        response = await revoke_access_token.aexecute(request)

        # Assertions
        assert response.success is True
        assert refresh_token.revoked_at is None
        assert refresh_token.expired_at >= get_utc_now()

        # Verify interactions
        mock_collection.find_one.assert_called_once_with({"_id": mock_refresh_token_id})
        mock_jwt_service.verify_password.assert_called_once_with(mock_access_token, refresh_token.hashed_access_token)
        mock_collection.update_one.call_count == 1
        call_args = mock_collection.update_one.call_args_list[0]
        assert call_args[0][0] == {"_id": mock_refresh_token_id}

    @pytest.mark.asyncio
    async def test_aexecute_no_refresh_token_found_throw_exception(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_db, mock_logger, mock_collection = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = UUID("3f7c4e8b-5e4d-4326-9fd7-bcf8d470cb10")

        # Mock collection
        mock_collection.configure_mock(find_one=Mock(return_value=None))

        # Mock jwt_service
        mock_jwt_service.configure_mock(
            verify_password=Mock(return_value=True),
        )

        # Initialize the component
        revoke_access_token = RevokeRefreshToken(
            db=mock_db,
            jwt_service=mock_jwt_service,
            logger=mock_logger,
        )

        request = RevokeRefreshToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)
        response = await revoke_access_token.aexecute(request)

        # Assertions
        assert response.success is False

        # Verify interactions
        mock_collection.find_one.assert_called_once_with({"_id": mock_refresh_token_id})

    @pytest.mark.asyncio
    async def test_aexecute_fail_hashed_access_token_verification_throw_exception(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_db, mock_logger, mock_collection = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = UUID("3f7c4e8b-5e4d-4326-9fd7-bcf8d470cb10")

        refresh_token = RefreshTokenModel(
            hashed_access_token="hashed_access_token",
            expired_at=get_utc_now() + timedelta(days=1),
            revoked_at=None,
        )

        # Mock collection
        mock_collection.configure_mock(find_one=Mock(return_value=refresh_token.model_dump(by_alias=True)))

        # Mock jwt_service
        mock_jwt_service.configure_mock(
            verify_password=Mock(return_value=False),
        )

        # Initialize the component
        revoke_access_token = RevokeRefreshToken(
            db=mock_db,
            jwt_service=mock_jwt_service,
            logger=mock_logger,
        )

        request = RevokeRefreshToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)
        response = await revoke_access_token.aexecute(request)

        # Assertions
        assert response.success is False

        # Verify interactions
        mock_collection.find_one.assert_called_once_with({"_id": mock_refresh_token_id})
        mock_jwt_service.verify_password.assert_called_once_with(mock_access_token, refresh_token.hashed_access_token)

    @pytest.mark.asyncio
    async def test_aexecute_refresh_token_already_revoked_throw_exception(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_db, mock_logger, mock_collection = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = UUID("3f7c4e8b-5e4d-4326-9fd7-bcf8d470cb10")

        refresh_token = RefreshTokenModel(
            hashed_access_token="hashed_access_token",
            expired_at=get_utc_now() + timedelta(days=1),
            revoked_at=get_utc_now() - timedelta(hours=12),
        )

        # Mock collection
        mock_collection.configure_mock(find_one=Mock(return_value=refresh_token.model_dump(by_alias=True)))

        # Mock jwt_service
        mock_jwt_service.configure_mock(
            verify_password=Mock(return_value=True),
        )

        # Initialize the component
        revoke_access_token = RevokeRefreshToken(
            db=mock_db,
            jwt_service=mock_jwt_service,
            logger=mock_logger,
        )

        request = RevokeRefreshToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)
        response = await revoke_access_token.aexecute(request)

        # Assertions
        assert response.success is False
        assert refresh_token.revoked_at is not None

        # Verify interactions
        mock_collection.find_one.assert_called_once_with({"_id": mock_refresh_token_id})
        mock_jwt_service.verify_password.assert_called_once_with(mock_access_token, refresh_token.hashed_access_token)

    @pytest.mark.asyncio
    async def test_aexecute_refresh_token_already_expired_throw_exception(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_db, mock_logger, mock_collection = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = UUID("3f7c4e8b-5e4d-4326-9fd7-bcf8d470cb10")

        refresh_token = RefreshTokenModel(
            hashed_access_token="hashed_access_token",
            expired_at=get_utc_now() - timedelta(days=1),
            revoked_at=None,
        )

        # Mock collection
        mock_collection.configure_mock(find_one=Mock(return_value=refresh_token.model_dump(by_alias=True)))

        # Mock jwt_service
        mock_jwt_service.configure_mock(
            verify_password=Mock(return_value=True),
        )

        # Initialize the component
        revoke_access_token = RevokeRefreshToken(
            db=mock_db,
            jwt_service=mock_jwt_service,
            logger=mock_logger,
        )

        request = RevokeRefreshToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)
        response = await revoke_access_token.aexecute(request)

        # Assertions
        assert response.success is False
        assert refresh_token.revoked_at is None
        assert refresh_token.expired_at <= get_utc_now()

        # Verify interactions
        mock_collection.find_one.assert_called_once_with({"_id": mock_refresh_token_id})
        mock_jwt_service.verify_password.assert_called_once_with(mock_access_token, refresh_token.hashed_access_token)
