from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from ....common.auth import TokenData
from ....common.models import OrganizationModel, UserModel, UserRole
from ....components.authenticate.authenticate_user import AuthenticateUser
from ....components.authenticate.create_refresh_token import CreateRefreshToken
from ....components.organizations import GetUserDefaultOrganization
from ....components.users import GetUserByEmail
from ....exceptions import BadRequestError

MockSetUp = tuple[Mock, Mock, Mock, Mock, Mock, Mock]


@pytest.fixture
def mocks() -> MockSetUp:
    mock_get_user_by_email = Mock()
    mock_jwt_service = Mock()
    mock_create_refresh_token = Mock()
    mock_db = Mock()
    mock_logger = Mock()
    mock_get_default_organization = Mock()
    return (
        mock_get_user_by_email,
        mock_jwt_service,
        mock_create_refresh_token,
        mock_db,
        mock_logger,
        mock_get_default_organization,
    )


class TestAuthenticateUser:
    @pytest.mark.asyncio
    async def test_aexecute_success(self, mocks: MockSetUp) -> None:
        (
            mock_get_user_by_email,
            mock_jwt_service,
            mock_create_refresh_token,
            mock_db,
            mock_logger,
            mock_get_default_organization,
        ) = mocks

        mock_user = UserModel(
            email="johndoe@gmail.com",
            username="johndoe",
            hashed_password="hashed_password",
            role=UserRole.OrganizationMember,
        )
        mock_get_user_by_email.configure_mock(aexecute=AsyncMock(return_value=GetUserByEmail.Response(user=mock_user)))

        mock_access_token = "access_token"
        mock_refresh_token_id = UUID("12345678-1234-5678-1234-567812345678")
        default_organization = OrganizationModel(
            name="test_org_name", avatar_url="http://test.example.com", owner_id=mock_user.id, is_default=True
        )
        mock_get_default_organization.configure_mock(
            aexecute=AsyncMock(return_value=GetUserDefaultOrganization.Response(organization=default_organization))
        )
        mock_user_token_data = TokenData(
            user_id=mock_user.id,
            username=mock_user.username,
            email=mock_user.email,
            role=UserRole.OrganizationAdmin,  # always role admin here <- not user.role
            organization_id=default_organization.id,
            sub=mock_user.email,
            exp=0,
        )
        mock_jwt_service.configure_mock(
            verify_password=Mock(return_value=True),
            create_user_token_data=Mock(return_value=mock_user_token_data),
            encode_jwt_token=Mock(return_value=mock_access_token),
        )
        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_refresh_token_id))
        )

        authenticate_user = AuthenticateUser(
            get_user_by_email=mock_get_user_by_email,
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
            get_default_organization=mock_get_default_organization,
        )

        authenticate_request = AuthenticateUser.Request(email=mock_user.email, password="password")
        authenticate_response = await authenticate_user.aexecute(authenticate_request)

        assert authenticate_response is not None
        assert authenticate_response.access_token == mock_access_token
        assert authenticate_response.refresh_token_id == mock_refresh_token_id

        mock_get_user_by_email.aexecute.assert_called_once_with(
            GetUserByEmail.Request(email=authenticate_request.email)
        )
        mock_jwt_service.verify_password.assert_called_once_with("password", "hashed_password")
        mock_jwt_service.create_user_token_data.assert_called_once_with(
            user=mock_user, user_role=UserRole.OrganizationAdmin, organization_id=default_organization.id
        )
        mock_jwt_service.encode_jwt_token.assert_called_once_with(mock_user_token_data)
        mock_create_refresh_token.aexecute.assert_called_once_with(
            CreateRefreshToken.Request(access_token=mock_access_token)
        )
        mock_get_default_organization.aexecute.assert_called_once_with(
            GetUserDefaultOrganization.Request(owner_id=mock_user.id)
        )

    @pytest.mark.asyncio
    async def test_aexecute_user_not_found(self, mocks: MockSetUp) -> None:
        (
            mock_get_user_by_email,
            mock_jwt_service,
            mock_create_refresh_token,
            mock_db,
            mock_logger,
            mock_get_default_organization,
        ) = mocks

        mock_get_user_by_email.configure_mock(aexecute=AsyncMock(return_value=GetUserByEmail.Response(user=None)))
        mock_get_default_organization.configure_mock(aexecute=AsyncMock(return_value=None))

        authenticate_user = AuthenticateUser(
            get_user_by_email=mock_get_user_by_email,
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
            get_default_organization=mock_get_default_organization,
        )

        authenticate_request = AuthenticateUser.Request(email="nonexistent@gmail.com", password="password")

        with pytest.raises(BadRequestError, match="User with email nonexistent@gmail.com not found."):
            await authenticate_user.aexecute(authenticate_request)

        mock_get_user_by_email.aexecute.assert_called_once_with(
            GetUserByEmail.Request(email=authenticate_request.email)
        )
        mock_jwt_service.encode_jwt_token.assert_not_called()
        mock_create_refresh_token.aexecute.assert_not_called()

    @pytest.mark.asyncio
    async def test_aexecute_incorrect_password(self, mocks: MockSetUp) -> None:
        (
            mock_get_user_by_email,
            mock_jwt_service,
            mock_create_refresh_token,
            mock_db,
            mock_logger,
            mock_get_default_organization,
        ) = mocks

        mock_user = UserModel(
            email="johndoe@gmail.com",
            username="johndoe",
            hashed_password="hashed_password",
            role=UserRole.OrganizationMember,
        )
        mock_get_user_by_email.configure_mock(aexecute=AsyncMock(return_value=GetUserByEmail.Response(user=mock_user)))
        mock_jwt_service.configure_mock(verify_password=Mock(return_value=False))
        default_organization = OrganizationModel(
            name="test_org_name", avatar_url="http://test.example.com", owner_id=mock_user.id, is_default=True
        )
        mock_get_default_organization.configure_mock(
            aexecute=AsyncMock(return_value=GetUserDefaultOrganization.Response(organization=default_organization))
        )

        authenticate_user = AuthenticateUser(
            get_user_by_email=mock_get_user_by_email,
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
            get_default_organization=mock_get_default_organization,
        )

        authenticate_request = AuthenticateUser.Request(email=mock_user.email, password="wrong_password")

        with pytest.raises(BadRequestError, match="Password for user johndoe@gmail.com is incorrect."):
            await authenticate_user.aexecute(authenticate_request)

        mock_get_user_by_email.aexecute.assert_called_once_with(
            GetUserByEmail.Request(email=authenticate_request.email)
        )
        mock_jwt_service.verify_password.assert_called_once_with("wrong_password", "hashed_password")
        mock_jwt_service.encode_jwt_token.assert_not_called()
        mock_create_refresh_token.aexecute.assert_not_called()
