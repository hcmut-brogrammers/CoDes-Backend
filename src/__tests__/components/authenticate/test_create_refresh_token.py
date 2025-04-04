from unittest.mock import Mock

import pytest

from ....common.models import RefreshTokenModel
from ....components.authenticate.create_refresh_token import CreateRefreshToken
from ....exceptions import InternalServerError
from ...utils.common import generate_uuid, get_utc_now

MockSetUp = tuple[Mock, Mock, Mock]


@pytest.fixture
def mocks() -> MockSetUp:
    mock_jwt_service = Mock()
    mock_db = Mock()
    mock_logger = Mock()
    return mock_jwt_service, mock_db, mock_logger


class TestCreateRefreshToken:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_db, mock_logger = mocks

        mock_hashed_access_token = "hashed_access_token"
        mock_refresh_token_id = generate_uuid()
        mock_refresh_token = RefreshTokenModel(
            _id=mock_refresh_token_id,
            hashed_access_token=mock_hashed_access_token,
            expired_at=get_utc_now(),
            revoked_at=None,
        )

        mock_jwt_service.hash.return_value = mock_hashed_access_token
        mock_collection = Mock()
        mock_db.get_collection.return_value = mock_collection
        mock_collection.insert_one.return_value.inserted_id = mock_refresh_token_id
        mock_collection.find_one.return_value = mock_refresh_token.model_dump()

        create_refresh_token = CreateRefreshToken(jwt_service=mock_jwt_service, db=mock_db, logger=mock_logger)

        request = CreateRefreshToken.Request(access_token="access_token")
        response = await create_refresh_token.aexecute(request)

        assert response.refresh_token_id == mock_refresh_token_id
        mock_jwt_service.hash.assert_called_once_with("access_token")
        mock_collection.insert_one.assert_called_once()
        mock_collection.find_one.assert_called_once_with({"_id": mock_refresh_token_id})

    @pytest.mark.asyncio
    async def test_aexecute_failure_to_retrieve_token(self, mocks: MockSetUp) -> None:
        mock_jwt_service, mock_db, mock_logger = mocks

        mock_hashed_access_token = "hashed_access_token"
        mock_refresh_token_id = "mock_refresh_token_id"

        mock_jwt_service.hash.return_value = mock_hashed_access_token
        mock_collection = Mock()
        mock_db.get_collection.return_value = mock_collection
        mock_collection.insert_one.return_value.inserted_id = mock_refresh_token_id
        mock_collection.find_one.return_value = None

        create_refresh_token = CreateRefreshToken(jwt_service=mock_jwt_service, db=mock_db, logger=mock_logger)

        request = CreateRefreshToken.Request(access_token="access_token")

        with pytest.raises(InternalServerError, match="Failed to create refresh token."):
            await create_refresh_token.aexecute(request)

        mock_jwt_service.hash.assert_called_once_with("access_token")
        mock_collection.insert_one.assert_called_once()
        mock_collection.find_one.assert_called_once_with({"_id": mock_refresh_token_id})
