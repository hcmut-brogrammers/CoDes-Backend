from datetime import timedelta
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest

from ....common.auth import TokenData
from ....common.models import UserRole
from ....common.models.organization import OrganizationModel
from ....components.authenticate.create_refresh_token import CreateRefreshToken
from ....components.authenticate.refresh_access_token import RefreshAccessToken
from ....components.organizations.get_organization_by_id import GetOrganizationById
from ....components.organizations.switch_organization import SwitchOrganization
from ....exceptions import BadRequestError
from ...utils.common import get_utc_now

MockSetUp = tuple[Mock, AsyncMock, Mock, Mock, AsyncMock, AsyncMock, Mock]


@pytest.fixture
def mocks() -> MockSetUp:
    mock_jwt_service = Mock()
    mock_create_refresh_token = AsyncMock()
    mock_db = Mock()
    mock_logger = Mock()
    mock_refresh_token_collection = AsyncMock()
    mock_get_organization = AsyncMock()
    mock_user_context = Mock()
    return (
        mock_jwt_service,
        mock_create_refresh_token,
        mock_db,
        mock_logger,
        mock_refresh_token_collection,
        mock_get_organization,
        mock_user_context,
    )


class TestRefreshAccessToken:
    @pytest.mark.asyncio
    async def test_aexecute_success_with_role_member_for_admin(self, mocks: MockSetUp) -> None:
        (
            mock_jwt_service,
            mock_create_refresh_token,
            mock_db,
            mock_logger,
            mock_refresh_token_collection,
            mock_get_organization,
            mock_user_context,
        ) = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = UUID("fcb8dbb3-2cd2-4411-8c69-7a5c58c7c225")
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = UUID("e3f5537c-94b1-4a5a-a6c2-bb4c8a9c57c1")
        mock_organization_id = UUID("38d2fcb0-6a4a-4682-8c6b-8bc06e8b8765")
        mock_user_id = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")

        token_data = TokenData(
            user_id=mock_user_id,
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=mock_organization_id,
            sub="johndoe",
            exp=int((get_utc_now() + timedelta(hours=1)).timestamp()),  # Convert datetime to UNIX timestamp
        )
        mock_jwt_service.configure_mock(
            encode_jwt_token=Mock(return_value=mock_new_access_token),
        )

        mock_db.get_collection.return_value = mock_refresh_token_collection
        mock_refresh_token_collection.configure_mock(
            find_one=Mock(
                return_value={
                    "_id": str(mock_refresh_token_id),
                    "hashed_access_token": "hashed_access_token",
                    "expired_at": get_utc_now() + timedelta(days=1),
                    "revoked_at": None,
                }
            ),
            update_one=Mock(return_value=None),
        )

        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_new_refresh_token_id))
        )

        mock_user_context = token_data

        mock_organization = OrganizationModel(
            name="switch-to organization",
            avatar_url="http://example.com",
            owner_id=mock_user_id,
            is_default=True,
        )
        mock_get_organization.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        refresh_access_token = SwitchOrganization(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
            get_organization=mock_get_organization,
            user_context=mock_user_context,
        )

        request = SwitchOrganization.Request(
            organization_id=mock_organization_id, refresh_token_id=mock_refresh_token_id
        )
        response = await refresh_access_token.aexecute(request)

        response_get_organization = await mock_get_organization.aexecute()
        assert response.access_token == mock_new_access_token
        assert response.refresh_token_id == mock_new_refresh_token_id
        # case: role admin
        assert response_get_organization.organization.owner_id == mock_user_context.user_id

        # Verificiation
        mock_refresh_token_collection.find_one.assert_called_once_with(
            {"_id": mock_refresh_token_id}  # Fixed query to match refresh token ID
        )
        mock_jwt_service.encode_jwt_token.assert_called_once_with(token_data)
        mock_refresh_token_collection.update_one.assert_called_once()
        mock_create_refresh_token.aexecute.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_success_with_role_member_for_user(self, mocks: MockSetUp) -> None:
        (
            mock_jwt_service,
            mock_create_refresh_token,
            mock_db,
            mock_logger,
            mock_refresh_token_collection,
            mock_get_organization,
            mock_user_context,
        ) = mocks

        mock_access_token = "access_token"
        mock_refresh_token_id = UUID("fcb8dbb3-2cd2-4411-8c69-7a5c58c7c225")
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = UUID("e3f5537c-94b1-4a5a-a6c2-bb4c8a9c57c1")
        mock_organization_id = UUID("38d2fcb0-6a4a-4682-8c6b-8bc06e8b8765")
        mock_user_id = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")

        token_data = TokenData(
            user_id=mock_user_id,
            username="johndoe",
            email="johndoe@gmail.com",
            role=UserRole.OrganizationAdmin,
            organization_id=mock_organization_id,
            sub="johndoe",
            exp=int((get_utc_now() + timedelta(hours=1)).timestamp()),  # Convert datetime to UNIX timestamp
        )
        mock_jwt_service.configure_mock(
            encode_jwt_token=Mock(return_value=mock_new_access_token),
        )

        mock_db.get_collection.return_value = mock_refresh_token_collection
        mock_refresh_token_collection.configure_mock(
            find_one=Mock(
                return_value={
                    "_id": str(mock_refresh_token_id),
                    "hashed_access_token": "hashed_access_token",
                    "expired_at": get_utc_now() + timedelta(days=1),
                    "revoked_at": None,
                }
            ),
            update_one=Mock(return_value=None),
        )

        mock_create_refresh_token.configure_mock(
            aexecute=AsyncMock(return_value=CreateRefreshToken.Response(refresh_token_id=mock_new_refresh_token_id))
        )

        mock_user_context = token_data

        mock_organization = OrganizationModel(
            name="switch-to organization",
            avatar_url="http://example.com",
            owner_id=uuid4(),
            is_default=True,
        )
        mock_get_organization.configure_mock(
            aexecute=AsyncMock(return_value=GetOrganizationById.Response(organization=mock_organization))
        )

        refresh_access_token = SwitchOrganization(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
            get_organization=mock_get_organization,
            user_context=mock_user_context,
        )

        request = SwitchOrganization.Request(
            organization_id=mock_organization_id, refresh_token_id=mock_refresh_token_id
        )
        response = await refresh_access_token.aexecute(request)

        response_get_organization = await mock_get_organization.aexecute()
        assert response.access_token == mock_new_access_token
        assert response.refresh_token_id == mock_new_refresh_token_id
        # case: role member
        assert response_get_organization.organization.owner_id != mock_user_context.user_id

        # Verificiation
        mock_refresh_token_collection.find_one.assert_called_once_with(
            {"_id": mock_refresh_token_id}  # Fixed query to match refresh token ID
        )
        mock_jwt_service.encode_jwt_token.assert_called_once_with(token_data)
        mock_refresh_token_collection.update_one.assert_called_once()
        mock_create_refresh_token.aexecute.assert_called_once()

    @pytest.mark.asyncio
    async def test_aexecute_no_refresh_token_found_throw_exception(self, mocks: MockSetUp) -> None:
        (
            mock_jwt_service,
            mock_create_refresh_token,
            mock_db,
            mock_logger,
            mock_refresh_token_collection,
            mock_get_organization,
            mock_user_context,
        ) = mocks

        mock_refresh_token_id = UUID("fcb8dbb3-2cd2-4411-8c69-7a5c58c7c225")
        mock_new_access_token = "new_access_token"
        mock_new_refresh_token_id = UUID("e3f5537c-94b1-4a5a-a6c2-bb4c8a9c57c1")
        mock_organization_id = UUID("38d2fcb0-6a4a-4682-8c6b-8bc06e8b8765")

        mock_db.get_collection.return_value = mock_refresh_token_collection
        mock_refresh_token_collection.configure_mock(
            find_one=Mock(return_value=None),
        )

        request = SwitchOrganization.Request(
            organization_id=mock_organization_id, refresh_token_id=mock_refresh_token_id
        )
        refresh_access_token = SwitchOrganization(
            jwt_service=mock_jwt_service,
            create_refresh_token=mock_create_refresh_token,
            db=mock_db,
            logger=mock_logger,
            get_organization=mock_get_organization,
            user_context=mock_user_context,
        )

        # Execute the component with exception
        with pytest.raises(BadRequestError):
            response = await refresh_access_token.aexecute(request)

        # Verificiation
        mock_refresh_token_collection.find_one.assert_called_once_with(
            {"_id": mock_refresh_token_id}  # Fixed query to match refresh token ID
        )
