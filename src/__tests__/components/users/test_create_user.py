from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from ....common.models import UserModel, UserRole
from ....components.users.create_user import CreateUser
from ....exceptions import InternalServerError

MockSetUp = tuple[Mock, Mock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_collection


class TestCreateUser:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        # Mock request and database response
        user = UserModel(
            username="johndoe",
            hashed_password="hashedpassword123",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationMember,
        )
        mock_inserted_id = uuid4()  # Use uuid4 to generate a valid UUID object
        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=mock_inserted_id)),
            find_one=Mock(return_value={**user.model_dump(), "_id": mock_inserted_id}),
        )

        # Initialize the component
        create_user = CreateUser(db=mock_db, logger=mock_logger)

        # Execute the component
        request = CreateUser.Request(**user.model_dump(exclude={"id"}))
        response = await create_user.aexecute(request)

        # Assertions
        assert response.created_user is not None
        assert response.created_user.id == mock_inserted_id
        assert response.created_user.username == user.username
        assert response.created_user.email == user.email
        assert response.created_user.role == user.role

        mock_collection.find_one.assert_called_once_with({"_id": mock_inserted_id})

    @pytest.mark.asyncio
    async def test_aexecute_when_user_not_found_throws_internal_server_error(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        # Mock request and database response
        user = UserModel(
            username="janedoe",
            hashed_password="hashedpassword456",
            email="janedoe@gmail.com",
            role=UserRole.OrganizationMember,
        )
        mock_inserted_id = uuid4()  # Use uuid4 to generate a valid UUID object
        mock_collection.configure_mock(
            insert_one=Mock(return_value=Mock(inserted_id=mock_inserted_id)),
            find_one=Mock(return_value=None),
        )

        # Initialize the component
        create_user = CreateUser(db=mock_db, logger=mock_logger)

        # Execute the component
        request = CreateUser.Request(**user.model_dump(exclude={"id"}))
        with pytest.raises(InternalServerError):
            await create_user.aexecute(request)

        # Verify interactions
        mock_collection.insert_one.assert_called_once()
        mock_collection.find_one.assert_called_once_with({"_id": mock_inserted_id})
