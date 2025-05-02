from unittest.mock import AsyncMock, Mock

import pytest

from ....common.models import UserModel
from ....components.users.get_me import GetMe
from ....components.users.get_user_by_id import GetUserById
from ....exceptions import NotFoundError
from ...utils.common import generate_uuid


class TestGetMe:
    @pytest.mark.asyncio
    async def test_aexecute_success(
        self,
        mock_get_user_by_id: Mock,
        mock_user_context: Mock,
        mock_db: Mock,
        mock_logger: Mock,
    ) -> None:
        # Arrange
        mock_user_id = generate_uuid()
        mock_user_context.configure_mock(user_id=mock_user_id)

        mock_user = UserModel(
            _id=mock_user_id,
            username="test_user",
            email="test_user@example.com",
            hashed_password="hashed_password",
        )
        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=GetUserById.Response(user=mock_user)))

        get_me = GetMe(
            get_user_by_id=mock_get_user_by_id,
            user_context=mock_user_context,
            db=mock_db,
            logger=mock_logger,
        )

        # Act
        response = await get_me.aexecute()

        # Assert
        user = response.user
        assert user.id == mock_user.id
        assert user.username == mock_user.username
        assert user.email == mock_user.email
        assert user.role == mock_user.role
        assert user.created_at == mock_user.created_at
        assert user.updated_at == mock_user.updated_at

    @pytest.mark.asyncio
    async def test_aexecute_user_not_found(
        self,
        mock_get_user_by_id: Mock,
        mock_user_context: Mock,
        mock_db: Mock,
        mock_logger: Mock,
    ) -> None:
        # Arrange
        mock_user_id = generate_uuid()
        mock_user_context.configure_mock(user_id=mock_user_id)

        mock_get_user_by_id.configure_mock(aexecute=AsyncMock(return_value=GetUserById.Response(user=None)))

        get_me = GetMe(
            get_user_by_id=mock_get_user_by_id,
            user_context=mock_user_context,
            db=mock_db,
            logger=mock_logger,
        )

        # Act & Assert
        with pytest.raises(NotFoundError, match=f"User with id {mock_user_id} not found."):
            await get_me.aexecute()
        mock_logger.error.assert_called_once_with(f"User with id {mock_user_id} not found.")
