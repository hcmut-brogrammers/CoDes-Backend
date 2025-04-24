from datetime import timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from ....common.auth import TokenData
from ....common.models import UserRole
from ....components.authenticate.create_refresh_token import CreateRefreshToken
from ....components.authenticate.refresh_access_token import RefreshAccessToken
from ....exceptions import BadRequestError
from ...utils.common import get_utc_now

MockSetUp = tuple[Mock, Mock, Mock, Mock, Mock]


@pytest.fixture
def mocks() -> MockSetUp:
    mock_jwt_service = Mock()
    mock_create_refresh_token = Mock()
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = Mock()
    return mock_jwt_service, mock_create_refresh_token, mock_db, mock_logger, mock_collection


class TestRefreshAccessToken:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_create_refresh_token, mock_db, mock_logger, mock_collection = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = uuid4()
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = uuid4()

        token_data = TokenData(
            user_id=uuid4(),
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=uuid4(),
            sub="johndoe",
            exp=int((get_utc_now() + timedelta(hours=1)).timestamp()),  # Convert datetime to UNIX timestamp
        )
        mock_jwt_service.configure_mock(
            decode_jwt_token=Mock(return_value=token_data),
            hash=Mock(return_value="hashed_access_token"),
            encode_jwt_token=Mock(return_value=mock_new_access_token),
        )

        mock_db.get_collection.return_value = mock_collection
        mock_collection.configure_mock(
            find_one=Mock(
                return_value={
                    "_id": str(mock_refresh_token_id),
                    "hashed_access_token": "hashed_access_token",
                    "expired_at": get_utc_now() + timedelta(days=1),
                    "revoked_at": None,
                }
            )
        )

        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_new_refresh_token_id))
        )

        refresh_access_token = RefreshAccessToken(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
        )

        request = RefreshAccessToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)
        response = await refresh_access_token.aexecute(request)

        assert response.access_token == mock_new_access_token
        assert response.refresh_token_id == mock_new_refresh_token_id

        mock_jwt_service.decode_jwt_token.assert_called_once_with(mock_access_token, verify_exp=False)
        mock_collection.find_one.assert_called_once_with(
            {"_id": mock_refresh_token_id}  # Fixed query to match refresh token ID
        )
        mock_create_refresh_token.aexecute.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_invalid_access_token_throw_exception(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_create_refresh_token, mock_db, mock_logger, mock_collection = mocks

        mock_jwt_service.configure_mock(decode_jwt_token=Mock(side_effect=ValueError()))

        refresh_access_token = RefreshAccessToken(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
        )

        request = RefreshAccessToken.Request(access_token="invalid_token", refresh_token_id=uuid4())

        with pytest.raises(BadRequestError, match="Failed to decode access token."):
            await refresh_access_token.aexecute(request)

        mock_jwt_service.decode_jwt_token.assert_called_once_with("invalid_token", verify_exp=False)

    @pytest.mark.asyncio
    async def test_aexecute_empty_access_token_throw_exception(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_create_refresh_token, mock_db, mock_logger, mock_collection = mocks

        mock_jwt_service.configure_mock(decode_jwt_token=Mock(return_value=None))

        refresh_access_token = RefreshAccessToken(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
        )

        request = RefreshAccessToken.Request(access_token="", refresh_token_id=uuid4())

        with pytest.raises(BadRequestError, match="Access token is empty."):
            await refresh_access_token.aexecute(request)

        mock_jwt_service.decode_jwt_token.assert_called_once_with("", verify_exp=False)

    @pytest.mark.asyncio
    async def test_aexecute_invalid_refresh_token_id_throw_exception(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_create_refresh_token, mock_db, mock_logger, mock_collection = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = uuid4()
        mock_new_access_token = "new_access_token"

        token_data = TokenData(
            user_id=uuid4(),
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=uuid4(),
            sub="johndoe",
            exp=int((get_utc_now() + timedelta(hours=1)).timestamp()),  # Convert datetime to UNIX timestamp
        )
        mock_jwt_service.configure_mock(
            decode_jwt_token=Mock(return_value=token_data),
            hash=Mock(return_value="hashed_access_token"),
            encode_jwt_token=Mock(return_value=mock_new_access_token),
        )

        mock_db.get_collection.return_value = mock_collection
        mock_collection.configure_mock(find_one=Mock(return_value=None))

        refresh_access_token = RefreshAccessToken(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
        )

        request = RefreshAccessToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)

        with pytest.raises(BadRequestError, match="Invalid refresh token id."):
            await refresh_access_token.aexecute(request)

        mock_jwt_service.decode_jwt_token.assert_called_once_with(mock_access_token, verify_exp=False)
        mock_collection.find_one.assert_called_once_with({"_id": mock_refresh_token_id})

    @pytest.mark.asyncio
    async def test_aexecute_invalid_hashed_access_token_throw_exception(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_create_refresh_token, mock_db, mock_logger, mock_collection = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = uuid4()
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = uuid4()

        token_data = TokenData(
            user_id=uuid4(),
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=uuid4(),
            sub="johndoe",
            exp=int((get_utc_now() + timedelta(hours=1)).timestamp()),  # Convert datetime to UNIX timestamp
        )
        mock_jwt_service.configure_mock(
            decode_jwt_token=Mock(return_value=token_data),
            hash=Mock(return_value="hashed_access_token"),
            encode_jwt_token=Mock(return_value=mock_new_access_token),
            verify_password=Mock(return_value=False),
        )

        mock_db.get_collection.return_value = mock_collection
        mock_collection.configure_mock(
            find_one=Mock(
                return_value={
                    "_id": str(mock_refresh_token_id),
                    "hashed_access_token": "hashed_access_token",
                    "expired_at": get_utc_now() + timedelta(days=1),
                    "revoked_at": None,
                }
            )
        )

        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_new_refresh_token_id))
        )

        refresh_access_token = RefreshAccessToken(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
        )

        request = RefreshAccessToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)

        with pytest.raises(BadRequestError, match="Hashed access token is invalid."):
            await refresh_access_token.aexecute(request)

        mock_jwt_service.decode_jwt_token.assert_called_once_with(mock_access_token, verify_exp=False)
        mock_collection.find_one.assert_called_once_with({"_id": mock_refresh_token_id})

        find_one_result = mock_collection.find_one()
        mock_jwt_service.verify_password.assert_called_once_with(
            request.access_token, find_one_result["hashed_access_token"]
        )

    @pytest.mark.asyncio
    async def test_aexecute_already_revoked_refresh_token_throw_exception(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_create_refresh_token, mock_db, mock_logger, mock_collection = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = uuid4()
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = uuid4()

        token_data = TokenData(
            user_id=uuid4(),
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=uuid4(),
            sub="johndoe",
            exp=int((get_utc_now() + timedelta(hours=1)).timestamp()),  # Convert datetime to UNIX timestamp
        )
        mock_jwt_service.configure_mock(
            decode_jwt_token=Mock(return_value=token_data),
            hash=Mock(return_value="hashed_access_token"),
            encode_jwt_token=Mock(return_value=mock_new_access_token),
            verify_password=Mock(return_value=True),
        )

        mock_db.get_collection.return_value = mock_collection
        mock_collection.configure_mock(
            find_one=Mock(
                return_value={
                    "_id": str(mock_refresh_token_id),
                    "hashed_access_token": "hashed_access_token",
                    "expired_at": get_utc_now() + timedelta(days=1),
                    "revoked_at": get_utc_now() - timedelta(seconds=18),
                }
            )
        )

        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_new_refresh_token_id))
        )

        refresh_access_token = RefreshAccessToken(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
        )

        request = RefreshAccessToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)

        with pytest.raises(BadRequestError, match="Refresh token is already revoked."):
            await refresh_access_token.aexecute(request)

        mock_jwt_service.decode_jwt_token.assert_called_once_with(mock_access_token, verify_exp=False)
        mock_collection.find_one.assert_called_once_with({"_id": mock_refresh_token_id})

        find_one_result = mock_collection.find_one()
        mock_jwt_service.verify_password.assert_called_once_with(
            request.access_token, find_one_result["hashed_access_token"]
        )

    @pytest.mark.asyncio
    async def test_aexecute_already_expired_refresh_token_throw_exception(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_create_refresh_token, mock_db, mock_logger, mock_collection = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = uuid4()
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = uuid4()

        token_data = TokenData(
            user_id=uuid4(),
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=uuid4(),
            sub="johndoe",
            exp=int((get_utc_now() + timedelta(hours=1)).timestamp()),  # Convert datetime to UNIX timestamp
        )
        mock_jwt_service.configure_mock(
            decode_jwt_token=Mock(return_value=token_data),
            hash=Mock(return_value="hashed_access_token"),
            encode_jwt_token=Mock(return_value=mock_new_access_token),
            verify_password=Mock(return_value=True),
        )

        mock_db.get_collection.return_value = mock_collection
        mock_collection.configure_mock(
            find_one=Mock(
                return_value={
                    "_id": str(mock_refresh_token_id),
                    "hashed_access_token": "hashed_access_token",
                    "expired_at": get_utc_now() - timedelta(seconds=18),
                    "revoked_at": None,
                }
            )
        )

        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_new_refresh_token_id))
        )

        refresh_access_token = RefreshAccessToken(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
        )

        request = RefreshAccessToken.Request(access_token=mock_access_token, refresh_token_id=mock_refresh_token_id)

        with pytest.raises(BadRequestError, match="Refresh token is expired."):
            await refresh_access_token.aexecute(request)

        mock_jwt_service.decode_jwt_token.assert_called_once_with(mock_access_token, verify_exp=False)
        mock_collection.find_one.assert_called_once_with({"_id": mock_refresh_token_id})

        find_one_result = mock_collection.find_one()
        mock_jwt_service.verify_password.assert_called_once_with(
            request.access_token, find_one_result["hashed_access_token"]
        )
