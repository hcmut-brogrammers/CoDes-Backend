from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from ....common.models import UserModel, UserRole
from ....components.authenticate import CreateRefreshToken, SignUp
from ....components.users import CreateUser, GetUserByEmail
from ....exceptions import BadRequestError
from ....services.jwt_service import TokenData

MockSetUp = tuple[Mock, Mock, Mock, Mock, Mock, Mock, Mock]


@pytest.fixture
def mocks() -> MockSetUp:
    mock_create_user = Mock()
    mock_get_user_by_email = Mock()
    mock_jwt_service = Mock()
    mock_create_refresh_token = Mock()
    mock_db = Mock()
    mock_logger = Mock()
    mock_collection = Mock()

    mock_db.configure_mock(get_collection=Mock(return_value=mock_collection))
    return (
        mock_create_user,
        mock_get_user_by_email,
        mock_jwt_service,
        mock_create_refresh_token,
        mock_db,
        mock_logger,
        mock_collection,
    )


class TestSignUp:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mocks: MockSetUp) -> None:
        (
            mock_create_user,
            mock_get_user_by_email,
            mock_jwt_service,
            mock_create_refresh_token,
            mock_db,
            mock_logger,
            mock_collection,
        ) = mocks

        mock_get_user_by_email.configure_mock(aexecute=AsyncMock(return_value=GetUserByEmail.Response(user=None)))
        mock_current_user = UserModel(
            email="johndoe@gmail.com",
            username="johndoe",
            hashed_password="hashed_password",
            role=UserRole.OrganizationMember,
        )
        mock_user_token_data = TokenData(
            user_id=mock_current_user.id,
            username=mock_current_user.username,
            email=mock_current_user.email,
            role=mock_current_user.role,
            sub=mock_current_user.username,
            exp=0,  # Convert datetime to UNIX timestamp
        )
        mock_current_user_response = CreateUser.Response(created_user=mock_current_user)
        mock_create_user.configure_mock(aexecute=AsyncMock(return_value=mock_current_user_response))

        mock_access_token = "access_token"
        mock_refresh_token_id = uuid4()
        mock_hashed_password = "hashed_password"
        mock_jwt_service.configure_mock(
            hash=Mock(return_value=mock_hashed_password),
            create_user_token_data=Mock(return_value=mock_user_token_data),
            encode_jwt_token=Mock(return_value=mock_access_token),
        )
        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_refresh_token_id))
        )

        sign_up = SignUp(
            create_user=mock_create_user,
            get_user_by_email=mock_get_user_by_email,
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
        )

        sign_up_request = SignUp.Request(
            email=mock_current_user.email,
            password="password",
            username=mock_current_user.username,
            role=mock_current_user.role,
        )
        sign_up_response = await sign_up.aexecute(sign_up_request)

        assert sign_up_response is not None
        assert sign_up_response.access_token == mock_access_token
        assert sign_up_response.refresh_token_id == mock_refresh_token_id

        mock_get_user_by_email.aexecute.assert_called_once_with(GetUserByEmail.Request(email=sign_up_request.email))
        mock_jwt_service.hash.assert_called_once_with("password")
        mock_create_user.aexecute.assert_called_once_with(
            CreateUser.Request(
                email=sign_up_request.email,
                hashed_password=mock_hashed_password,
                username=sign_up_request.username,
                role=sign_up_request.role,
            )
        )
        mock_jwt_service.create_user_token_data.assert_called_once_with(mock_current_user_response.created_user)
        mock_jwt_service.encode_jwt_token.assert_called_once_with(mock_user_token_data)
        mock_create_refresh_token.aexecute.assert_called_once_with(
            CreateRefreshToken.Request(access_token=mock_access_token)
        )

    @pytest.mark.asyncio
    async def test_aexecute_user_already_exists(self, mocks: MockSetUp) -> None:
        (
            mock_create_user,
            mock_get_user_by_email,
            mock_jwt_service,
            mock_create_refresh_token,
            mock_db,
            mock_logger,
            mock_collection,
        ) = mocks

        mock_existing_user = UserModel(
            email="johndoe@gmail.com",
            username="johndoe",
            hashed_password="hashed_password",
            role=UserRole.OrganizationMember,
        )
        mock_get_user_by_email.configure_mock(
            aexecute=AsyncMock(return_value=GetUserByEmail.Response(user=mock_existing_user))
        )

        sign_up = SignUp(
            create_user=mock_create_user,
            get_user_by_email=mock_get_user_by_email,
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
        )

        sign_up_request = SignUp.Request(
            email="johndoe@gmail.com",
            password="password",
            username="johndoe",
            role=UserRole.OrganizationMember,
        )

        with pytest.raises(BadRequestError, match="User with email johndoe@gmail.com already exists."):
            await sign_up.aexecute(sign_up_request)

        mock_get_user_by_email.aexecute.assert_called_once_with(GetUserByEmail.Request(email=sign_up_request.email))
        mock_jwt_service.hash.assert_not_called()
        mock_create_user.aexecute.assert_not_called()
        mock_jwt_service.encode_jwt_token.assert_not_called()
        mock_create_refresh_token.aexecute.assert_not_called()
