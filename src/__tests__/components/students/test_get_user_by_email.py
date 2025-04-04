from unittest.mock import AsyncMock, Mock

import pytest

from ....common.models import UserModel, UserRole
from ....components.users.get_user_by_email import GetUserByEmail
from ....constants.mongo import CollectionName
from ....exceptions import BadRequestError

MockSetUp = tuple[Mock, Mock]


@pytest.fixture
def mocks() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    return mock_db, mock_logger


class TestGetUserByEmail:
    @pytest.mark.asyncio
    async def test_aexecute_user_found(self, mocks: MockSetUp) -> None:
        mock_db, mock_logger = mocks
        mock_collection = Mock()
        mock_user = UserModel(
            email="johndoe@gmail.com",
            username="johndoe",
            hashed_password="hashed_password",
            role=UserRole.OrganizationMember,
        )
        mock_collection.find_one = Mock(return_value=mock_user.model_dump(by_alias=True))
        mock_db.get_collection = Mock(return_value=mock_collection)

        get_user_by_email = GetUserByEmail(db=mock_db, logger=mock_logger)
        request = GetUserByEmail.Request(email="johndoe@gmail.com")
        response = await get_user_by_email.aexecute(request)

        assert response.user is not None
        assert response.user.email == mock_user.email
        assert response.user.username == mock_user.username

        mock_collection.find_one.assert_called_once_with({"email": request.email})

    @pytest.mark.asyncio
    async def test_aexecute_user_not_found(self, mocks: MockSetUp) -> None:
        mock_db, mock_logger = mocks
        mock_collection = Mock()
        mock_collection.find_one = Mock(return_value=None)
        mock_db.get_collection = Mock(return_value=mock_collection)

        get_user_by_email = GetUserByEmail(db=mock_db, logger=mock_logger)
        request = GetUserByEmail.Request(email="nonexistent@gmail.com")
        response = await get_user_by_email.aexecute(request)

        assert response.user is None

        mock_collection.find_one.assert_called_once_with({"email": request.email})
