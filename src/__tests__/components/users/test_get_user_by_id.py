from unittest.mock import AsyncMock, Mock

import pytest

from ....common.models import UserModel, UserRole
from ....components.users.get_user_by_id import GetUserById
from ....utils.common import generate_uuid

MockSetUp = tuple[Mock, Mock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_collection


class TestGetUserById:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_setup: MockSetUp) -> None:
        # Arrange
        mock_db, mock_logger, mock_collection = mock_setup
        user_id = generate_uuid()
        mock_user = UserModel(
            _id=user_id,
            username="johndoe",
            email="johndoe@gmail.com",
            hashed_password="hashedpassword123",
            role=UserRole.OrganizationMember,
        )
        mock_user_data = mock_user.model_dump(by_alias=True)
        mock_collection.configure_mock(find_one=Mock(return_value=mock_user_data))

        # Act
        get_user_by_id = GetUserById(db=mock_db, logger=mock_logger)
        request = GetUserById.Request(user_id=user_id)
        response = await get_user_by_id.aexecute(request)

        # Assert
        assert response.user is not None
        assert response.user.id == user_id
        assert response.user.username == mock_user.username
        assert response.user.email == mock_user.email
        assert response.user.role == mock_user.role

        mock_collection.find_one.assert_called_once_with({"_id": user_id})

    @pytest.mark.asyncio
    async def test_aexecute_when_user_not_found_throws_not_found_error(self, mock_setup: MockSetUp) -> None:
        # Arrange
        mock_db, mock_logger, mock_collection = mock_setup
        user_id = generate_uuid()
        mock_collection.configure_mock(find_one=Mock(return_value=None))

        # Act
        get_user_by_id = GetUserById(db=mock_db, logger=mock_logger)
        response = await get_user_by_id.aexecute(GetUserById.Request(user_id=user_id))

        # Assert
        assert response.user is None
