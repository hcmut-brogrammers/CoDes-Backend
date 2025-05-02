from unittest.mock import AsyncMock, Mock

import pytest

from ....common.models import UserModel, UserRole
from ....components.users.get_users_by_email_fragment import GetUserByEmailFragment
from ....utils.common import generate_uuid

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
        # Arrange
        mock_db, mock_logger, mock_collection = mock_setup
        mock_users = [
            UserModel(
                _id=generate_uuid(),
                username="johndoe1",
                email="johndoe1@gmail.com",
                hashed_password="johndoe1",
                role=UserRole.OrganizationMember,
            ),
            UserModel(
                _id=generate_uuid(),
                username="johndoe2",
                email="johndoe2@gmail.com",
                hashed_password="johndoe2",
                role=UserRole.OrganizationMember,
            ),
            UserModel(
                _id=generate_uuid(),
                username="johndoe3",
                email="johndoe3@gmail.com",
                hashed_password="johndoe3",
                role=UserRole.OrganizationMember,
            ),
            UserModel(
                _id=generate_uuid(),
                username="johndoe4",
                email="johndoe4@gmail.com",
                hashed_password="johndoe4",
                role=UserRole.OrganizationMember,
            ),
        ]
        mock_users_data = [user.model_dump(by_alias=True) for user in mock_users]
        mock_collection.configure_mock(find=Mock(return_value=mock_users_data))

        # Act
        get_user_by_email_fragment = GetUserByEmailFragment(db=mock_db, logger=mock_logger)
        request = GetUserByEmailFragment.Request(email_fragment="doe")
        response = await get_user_by_email_fragment.aexecute(request)

        # Assert
        assert len(response.users) == len(mock_users)
        for user, mock_user in zip(response.users, mock_users):
            assert user is not None
            assert user.id == mock_user.id
            assert user.username == mock_user.username
            assert user.email == mock_user.email

        regex_pattern = f".*{request.email_fragment}.*"
        mock_collection.find.assert_called_once_with({"email": {"$regex": regex_pattern, "$options": "i"}})

    @pytest.mark.asyncio
    async def test_aexecute_no_user_found_return_empty_users_list(self, mock_setup: MockSetUp) -> None:
        # Assert
        mock_db, mock_logger, mock_collection = mock_setup
        mock_collection.configure_mock(find=Mock(return_value=None))

        # Act
        request = GetUserByEmailFragment.Request(email_fragment="anything HERE")
        get_user_by_email_fragment = GetUserByEmailFragment(db=mock_db, logger=mock_logger)
        request = GetUserByEmailFragment.Request(email_fragment="doe")
        response = await get_user_by_email_fragment.aexecute(request)

        # Assert
        assert len(response.users) == 0

        regex_pattern = f".*{request.email_fragment}.*"
        mock_collection.find.assert_called_once_with({"email": {"$regex": regex_pattern, "$options": "i"}})
