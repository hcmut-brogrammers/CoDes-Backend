from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from ....components.users.delete_user_by_id import DeleteUserById
from ....exceptions import InternalServerError, NotFoundError

MockSetUp = tuple[Mock, Mock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_collection


class TestDeleteUserById:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        # Mock request and database response
        user_id = uuid4()  # Use uuid4 to generate a valid UUID object
        mock_collection.configure_mock(delete_one=Mock(return_value=Mock(deleted_count=1)))

        # Initialize the component
        delete_user_by_id = DeleteUserById(db=mock_db, logger=mock_logger)

        # Execute the component
        request = DeleteUserById.Request(user_id=user_id)
        response = await delete_user_by_id.aexecute(request)

        # Assertions
        assert response.success is True

        mock_collection.delete_one.assert_called_once_with({"_id": user_id})

    @pytest.mark.asyncio
    async def test_aexecute_when_user_not_found_throws_not_found_error(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        # Mock request and database response
        user_id = uuid4()  # Use uuid4 to generate a valid UUID object
        mock_collection.configure_mock(delete_one=Mock(return_value=Mock(deleted_count=0)))

        # Initialize the component
        delete_user_by_id = DeleteUserById(db=mock_db, logger=mock_logger)

        # Execute the component
        request = DeleteUserById.Request(user_id=user_id)
        with pytest.raises(NotFoundError):
            await delete_user_by_id.aexecute(request)

        # Verify interactions
        mock_collection.delete_one.assert_called_once_with({"_id": user_id})

    @pytest.mark.asyncio
    async def test_aexecute_with_unexpected_deletion_count_throws_internal_server_error(
        self, mock_setup: MockSetUp
    ) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        # Mock request and database response
        user_id = uuid4()  # Use uuid4 to generate a valid UUID object
        mock_collection.configure_mock(delete_one=Mock(return_value=Mock(deleted_count=2)))

        # Initialize the component
        delete_user_by_id = DeleteUserById(db=mock_db, logger=mock_logger)

        # Execute the component
        request = DeleteUserById.Request(user_id=user_id)
        with pytest.raises(InternalServerError):
            await delete_user_by_id.aexecute(request)

        # Verify interactions
        mock_collection.delete_one.assert_called_once_with({"_id": user_id})
