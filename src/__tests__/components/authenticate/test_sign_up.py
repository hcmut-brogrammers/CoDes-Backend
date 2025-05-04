from unittest.mock import AsyncMock, Mock

import pytest

from ....common.auth import TokenData
from ....common.models import OrganizationModel, UserModel, UserRole
from ....components.authenticate import CreateRefreshToken, SignUp
from ....components.organizations import CreateUserDefaultOrganization
from ....components.users import CreateUser, GetUserByEmail
from ....exceptions import BadRequestError
from ...utils.common import generate_uuid


@pytest.fixture
def mock_user() -> UserModel:
    return UserModel(
        email="johndoe@gmail.com",
        username="johndoe",
        hashed_password="hashed_password",
        role=UserRole.OrganizationMember,
    )


class TestSignUp:
    @pytest.mark.asyncio
    async def test_aexecute_success(
        self,
        mock_create_user: Mock,
        mock_get_user_by_email: Mock,
        mock_jwt_service: Mock,
        mock_create_refresh_token: Mock,
        mock_logger: Mock,
        mock_create_user_default_organization: Mock,
        mock_user: UserModel,
    ) -> None:
        # Arrange
        mock_get_user_by_email.configure_mock(aexecute=AsyncMock(return_value=GetUserByEmail.Response(user=None)))
        mock_organization = OrganizationModel(
            name="name_default_org", avatar_url=None, owner_id=mock_user.id, is_default=True
        )
        mock_create_user_default_organization.configure_mock(
            aexecute=AsyncMock(
                return_value=CreateUserDefaultOrganization.Response(created_organization=mock_organization)
            )
        )

        mock_user_token_data = TokenData(
            user_id=mock_user.id,
            username=mock_user.username,
            email=mock_user.email,
            role=mock_user.role,
            organization_id=mock_organization.id,
            sub=mock_user.username,
            exp=0,
        )
        mock_create_user.configure_mock(aexecute=AsyncMock(return_value=CreateUser.Response(created_user=mock_user)))

        mock_access_token = "access_token"
        mock_refresh_token_id = generate_uuid()
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
            logger=mock_logger,
            create_default_organization=mock_create_user_default_organization,
        )

        sign_up_request = SignUp.Request(
            email=mock_user.email,
            password="password",
            username=mock_user.username,
        )

        # Act
        sign_up_response = await sign_up.aexecute(sign_up_request)

        # Assert
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
                role=UserRole.OrganizationAdmin,
            )
        )

        mock_create_user_default_organization.aexecute.assert_called_once_with(
            CreateUserDefaultOrganization.Request(
                owner_id=mock_user.id,
                owner_username=mock_user.username,
            )
        )
        mock_jwt_service.create_user_token_data.assert_called_once_with(
            user=mock_user,
            user_role=UserRole.OrganizationAdmin,
            organization_id=mock_organization.id,
        )
        mock_jwt_service.encode_jwt_token.assert_called_once_with(mock_user_token_data)
        mock_create_refresh_token.aexecute.assert_called_once_with(
            CreateRefreshToken.Request(access_token=mock_access_token)
        )

    @pytest.mark.asyncio
    async def test_aexecute_user_already_exists(
        self,
        mock_create_user: Mock,
        mock_get_user_by_email: Mock,
        mock_jwt_service: Mock,
        mock_create_refresh_token: Mock,
        mock_logger: Mock,
        mock_create_user_default_organization: Mock,
        mock_user: UserModel,
    ) -> None:
        # Arrange
        mock_get_user_by_email.configure_mock(aexecute=AsyncMock(return_value=GetUserByEmail.Response(user=mock_user)))

        sign_up = SignUp(
            create_user=mock_create_user,
            get_user_by_email=mock_get_user_by_email,
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            logger=mock_logger,
            create_default_organization=mock_create_user_default_organization,
        )

        sign_up_request = SignUp.Request(
            email=mock_user.email,
            password="password",
            username=mock_user.username,
        )

        # Act & Assert
        with pytest.raises(BadRequestError, match=f"User with email {mock_user.email} already exists."):
            await sign_up.aexecute(sign_up_request)

        mock_get_user_by_email.aexecute.assert_called_once_with(GetUserByEmail.Request(email=sign_up_request.email))
        mock_jwt_service.hash.assert_not_called()
        mock_create_user.aexecute.assert_not_called()
        mock_jwt_service.encode_jwt_token.assert_not_called()
        mock_create_refresh_token.aexecute.assert_not_called()
