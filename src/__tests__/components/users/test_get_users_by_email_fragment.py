from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from ....components.users.get_users_by_email_fragment import GetUserByEmailFragment
from ....exceptions import NotFoundError

MockSetUp = tuple[Mock, Mock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_collection


class TestGetUserByEmailFragment:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        # Mock request and database response
        users_data = [
            {
                "_id": uuid4(),
                "username": "johndoe0",
                "hashed_password": "hashedpassword123",
                "email": "johndoe@gmail.com",
                "role": "OrganizationMember",
            },
            {
                "_id": uuid4(),
                "username": "johndoe1",
                "hashed_password": "hashedpassword123",
                "email": "johnDoE@gmail.com",
                "role": "OrganizationMember",
            },
            {
                "_id": uuid4(),
                "username": "johndoe2",
                "hashed_password": "hashedpassword123",
                "email": "john@gmail.dOe.com",
                "role": "OrganizationMember",
            },
            {
                "_id": uuid4(),
                "username": "johndoe3",
                "hashed_password": "hashedpassword123",
                "email": "john@gmail.DOEdoEdoe",
                "role": "OrganizationMember",
            },
        ]
        mock_collection.configure_mock(find=Mock(return_value=users_data))

        # Initialize the component
        get_user_by_email_fragment = GetUserByEmailFragment(db=mock_db, logger=mock_logger)

        # Execute the component
        email_fragment = "doe"
        request = GetUserByEmailFragment.Request(email_fragment=email_fragment)
        response = await get_user_by_email_fragment.aexecute(request)

        # Assertions
        assert len(response.users) == len(users_data)
        for user, user_data in zip(response.users, users_data):
            assert user is not None
            assert user.id == user_data["_id"]
            assert user.username == user_data["username"]
            assert user.email == user_data["email"]
            assert user.role == user_data["role"]

        regex_pattern = f".*{request.email_fragment}.*"
        mock_collection.find.assert_called_once_with({"email": {"$regex": regex_pattern, "$options": "i"}})

    @pytest.mark.asyncio
    async def test_aexecute_no_user_found_return_empty_users_list(self, mock_setup: MockSetUp) -> None:
        # Setup mocks
        mock_db, mock_logger, mock_collection = mock_setup

        mock_collection.configure_mock(find=Mock(return_value=None))

        # Mock request and database response
        email_fragment = "anything HERE"
        request = GetUserByEmailFragment.Request(email_fragment=email_fragment)

        # Initialize the component
        get_user_by_email_fragment = GetUserByEmailFragment(db=mock_db, logger=mock_logger)

        # Execute the component
        request = GetUserByEmailFragment.Request(email_fragment="doe")
        response = await get_user_by_email_fragment.aexecute(request)

        # Assertions
        assert len(response.users) == 0

        regex_pattern = f".*{request.email_fragment}.*"
        mock_collection.find.assert_called_once_with({"email": {"$regex": regex_pattern, "$options": "i"}})
