from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from ....components.users.get_user_by_id import GetUserById
from ....exceptions import NotFoundError

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
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        # Mock request and database response
        user_id = uuid4()  # Use uuid4 to generate a valid UUID object
        user_data = {
            "_id": user_id,
            "username": "johndoe",
            "hashed_password": "hashedpassword123",
            "email": "johndoe@gmail.com",
            "role": "OrganizationMember",
        }
        mock_collection.configure_mock(find_one=Mock(return_value=user_data))

        # Initialize the component
        get_user_by_id = GetUserById(db=mock_db, logger=mock_logger)

        # Execute the component
        request = GetUserById.Request(user_id=user_id)
        response = await get_user_by_id.aexecute(request)

        # Assertions
        assert response.user is not None
        assert response.user.id == user_id
        assert response.user.username == user_data["username"]
        assert response.user.email == user_data["email"]
        assert response.user.role == user_data["role"]

        mock_collection.find_one.assert_called_once_with({"_id": user_id})

    @pytest.mark.asyncio
    async def test_aexecute_when_user_not_found_throws_not_found_error(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        # Mock request and database response
        user_id = uuid4()  # Use uuid4 to generate a valid UUID object
        mock_collection.configure_mock(find_one=Mock(return_value=None))

        # Initialize the component
        get_user_by_id = GetUserById(db=mock_db, logger=mock_logger)

        # Execute the component
        request = GetUserById.Request(user_id=user_id)
        with pytest.raises(NotFoundError):
            await get_user_by_id.aexecute(request)

        # Verify interactions
        mock_collection.find_one.assert_called_once_with({"_id": user_id})
