from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from ....common.models import UserModel, UserRole
from ....components.users.update_user import UpdateUser
from ....exceptions import BadRequestError, NotFoundError

MockSetUp = tuple[Mock, Mock, AsyncMock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = AsyncMock()
    mock_get_user_by_id = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_collection, mock_get_user_by_id


class TestUpdateUser:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_collection, mock_get_user_by_id = mock_setup

        # Mock request and database response
        user_id = uuid4()
        mock_user = UserModel(
            _id=user_id,
            username="oldusername",
            email="oldemail@gmail.com",
            hashed_password="hashedpassword123",
            role=UserRole.OrganizationMember,
        )
        update_data = {"username": "newusername", "email": "newemail@gmail.com"}
        mock_updated_user = mock_user.model_copy(update=update_data)
        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=Mock(user=mock_user)))
        mock_collection.configure_mock(update_one=Mock(return_value=None))

        # Initialize the component
        update_user = UpdateUser(get_user_by_id=mock_get_user_by_id, db=mock_db, logger=mock_logger)

        # Execute the component
        request = UpdateUser.Request(user_id=user_id, **update_data)
        response = await update_user.aexecute(request)

        # Assertions
        assert response.updated_user is not None
        assert response.updated_user.id == user_id
        assert response.updated_user.username == mock_updated_user.username
        assert response.updated_user.email == mock_updated_user.email

        # Verify interactions
        mock_collection.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_when_no_fields_to_update_throws_bad_request_error(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, _, mock_get_user_by_id = mock_setup

        # Initialize the component
        update_user = UpdateUser(get_user_by_id=mock_get_user_by_id, db=mock_db, logger=mock_logger)

        # Execute the component
        request = UpdateUser.Request(user_id=uuid4())
        with pytest.raises(BadRequestError):
            await update_user.aexecute(request)

    @pytest.mark.asyncio
    async def test_aexecute_when_user_not_found_throws_not_found_error(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, _, mock_get_user_by_id = mock_setup

        # Mock request and database response
        user_id = uuid4()
        update_data = {"username": "newusername"}
        mock_get_user_by_id.configure_mock(
            aexecute=AsyncMock(side_effect=NotFoundError(f"User with id {user_id} not found"))
        )

        # Initialize the component
        update_user = UpdateUser(get_user_by_id=mock_get_user_by_id, db=mock_db, logger=mock_logger)

        # Execute the component
        request = UpdateUser.Request(user_id=user_id, **update_data)
        with pytest.raises(NotFoundError):
            await update_user.aexecute(request)
