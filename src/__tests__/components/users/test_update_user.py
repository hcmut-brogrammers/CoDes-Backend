from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest

from ....common.models import UserModel, UserRole
from ....components.users import GetMe, GetUserById, UpdateUser
from ....exceptions import BadRequestError
from ....utils.common import generate_uuid

MockSetUp = tuple[Mock, Mock, AsyncMock, AsyncMock]


@pytest.fixture
def mock_setup() -> MockSetUp:
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = AsyncMock()
    mock_get_user_by_id = AsyncMock()
    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return mock_db, mock_logger, mock_collection, mock_get_user_by_id


@pytest.fixture
def mock_user_id() -> UUID:
    return generate_uuid()


class TestUpdateUser:
    @pytest.mark.asyncio
    async def test_aexecute_success(
        self,
        mock_db: Mock,
        mock_logger: Mock,
        mock_collection: Mock,
        mock_get_user_by_id: Mock,
        mock_user_id: UUID,
    ) -> None:
        # Arrange
        mock_user = UserModel(
            _id=mock_user_id,
            username="oldusername",
            email="oldemail@gmail.com",
            hashed_password="hashedpassword123",
            role=UserRole.OrganizationMember,
            joined_organizations=[],
        )
        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=Mock(user=mock_user)))

        mock_http_request = UpdateUser.HttpRequest(username="newusername")
        mock_updated_user = mock_user.model_copy(update=mock_http_request.model_dump())

        mock_collection.configure_mock(update_one=Mock(return_value=None))

        update_user = UpdateUser(get_user_by_id=mock_get_user_by_id, db=mock_db, logger=mock_logger)
        request = UpdateUser.Request(user_id=mock_user_id, **mock_http_request.model_dump())

        # Act
        response = await update_user.aexecute(request)

        # Assert
        assert type(response.updated_user) == GetMe.User
        assert response.updated_user is not None
        assert response.updated_user.id == mock_updated_user.id
        assert response.updated_user.username == mock_updated_user.username
        assert response.updated_user.email == mock_updated_user.email
        assert response.updated_user.role == mock_updated_user.role
        assert response.updated_user.joined_organizations == mock_updated_user.joined_organizations
        assert response.updated_user.created_at == mock_updated_user.created_at
        assert response.updated_user.updated_at != mock_updated_user.updated_at

        # Verify interactions
        mock_collection.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_when_no_fields_to_update_should_throw_bad_request_error(
        self, mock_db: Mock, mock_logger: Mock, mock_get_user_by_id: Mock
    ) -> None:
        # Arrange
        update_user = UpdateUser(get_user_by_id=mock_get_user_by_id, db=mock_db, logger=mock_logger)
        mock_http_request = UpdateUser.HttpRequest(username=None)

        # Act and Assert
        request = UpdateUser.Request(user_id=uuid4(), **mock_http_request.model_dump())
        with pytest.raises(BadRequestError):
            await update_user.aexecute(request)

    @pytest.mark.asyncio
    async def test_aexecute_when_user_not_found_should_throw_not_found_error(
        self, mock_db: Mock, mock_logger: Mock, mock_get_user_by_id: Mock, mock_user_id: UUID
    ) -> None:
        # Arrange
        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=GetUserById.Response(user=None)))

        update_user = UpdateUser(get_user_by_id=mock_get_user_by_id, db=mock_db, logger=mock_logger)
        mock_http_request = UpdateUser.HttpRequest(username="newusername")
        request = UpdateUser.Request(user_id=mock_user_id, **mock_http_request.model_dump())

        # Act and Assert
        with pytest.raises(BadRequestError):
            await update_user.aexecute(request)

        mock_get_user_by_id.aexecute.assert_called_once_with(GetUserById.Request(user_id=mock_user_id))
