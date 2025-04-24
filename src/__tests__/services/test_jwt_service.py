from datetime import timedelta
from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...common.auth import TokenData
from ...common.models import UserModel, UserRole
from ...services.jwt_service import JwtService
from ...utils.common import generate_uuid, get_utc_now


@pytest.fixture
def jwt_service() -> JwtService:
    mock_settings = Mock(JWT_SECRET_KEY="test_secret_key")
    mock_logger = Mock()
    return JwtService(settings=mock_settings, logger=mock_logger)


@pytest.fixture
def token_data() -> TokenData:
    token_data = TokenData(
        user_id=generate_uuid(),
        username="testuser",
        email="testuser@example.com",
        role=UserRole.OrganizationAdmin,
        organization_id=generate_uuid(),
        sub="testuser",
        exp=int((get_utc_now() + timedelta(hours=1)).timestamp()),
    )
    return token_data


@pytest.fixture
def expired_token_data() -> TokenData:
    token_data = TokenData(
        user_id=generate_uuid(),
        username="testuser",
        email="testuser@example.com",
        role=UserRole.OrganizationAdmin,
        organization_id=generate_uuid(),
        sub="testuser",
        exp=int((get_utc_now() - timedelta(hours=1)).timestamp()),
    )
    return token_data


def validate_decoded_token_data(decoded_token_data: TokenData, token_data: TokenData) -> None:
    assert decoded_token_data is not None
    assert decoded_token_data.username == token_data.username
    assert decoded_token_data.email == token_data.email
    assert decoded_token_data.role == token_data.role
    assert decoded_token_data.user_id == token_data.user_id
    assert decoded_token_data.organization_id == token_data.organization_id
    assert decoded_token_data.sub == token_data.sub
    assert decoded_token_data.exp == token_data.exp


def test_encode_jwt_token_success(jwt_service: JwtService, token_data: TokenData) -> None:
    token = jwt_service.encode_jwt_token(token_data)
    assert token is not None


def test_decode_jwt_token_success(jwt_service: JwtService, token_data: TokenData) -> None:
    token = jwt_service.encode_jwt_token(token_data)
    decoded_token_data = jwt_service.decode_jwt_token(token)
    validate_decoded_token_data(decoded_token_data, token_data)


def test_decode_jwt_token_with_expired_jwt_token_throws_exception(
    jwt_service: JwtService, expired_token_data: TokenData
) -> None:
    token = jwt_service.encode_jwt_token(expired_token_data)
    with pytest.raises(ValueError, match="JWT token has expired."):
        jwt_service.decode_jwt_token(token)


def test_decode_jwt_token_with_bypass_expired_jwt_token_success(
    jwt_service: JwtService, expired_token_data: TokenData
) -> None:
    expired_token = jwt_service.encode_jwt_token(expired_token_data)
    decoded_token_data = jwt_service.decode_jwt_token(expired_token, verify_exp=False)
    validate_decoded_token_data(decoded_token_data, expired_token_data)


def test_decode_jwt_token_with_invalid_token_throws_exception(jwt_service: JwtService) -> None:
    invalid_token = "invalid.token.value"
    with pytest.raises(ValueError, match="Error while decoding JWT token."):
        jwt_service.decode_jwt_token(invalid_token)


def test_hash_success(jwt_service: JwtService) -> None:
    password = "securepassword"
    hashed_password = jwt_service.hash(password)
    assert hashed_password != password


def test_hash_with_same_input_and_different_outputs_success(jwt_service: JwtService) -> None:
    password = "securepassword"
    hashed_password_1 = jwt_service.hash(password)
    hashed_password_2 = jwt_service.hash(password)
    assert hashed_password_1 != hashed_password_2


def test_verify_password_success(jwt_service: JwtService) -> None:
    password = "securepassword"
    hashed_password = jwt_service.hash(password)
    assert jwt_service.verify_password(password, hashed_password)


def test_create_user_token_data(jwt_service: JwtService) -> None:
    user = UserModel(
        _id=uuid4(),
        username="testuser",
        email="testuser@example.com",
        role=UserRole.OrganizationAdmin,
        hashed_password="hashed_password",
    )

    mock_role = UserRole.OrganizationAdmin
    mock_organization_id = generate_uuid()

    token_data = jwt_service.create_user_token_data(
        user,
        mock_role,
        mock_organization_id,
    )
    assert token_data is not None
    assert token_data.user_id == user.id
    assert token_data.username == user.username
    assert token_data.email == user.email
    assert token_data.role == UserRole.OrganizationAdmin
    assert token_data.sub == user.username
    assert token_data.exp is not None
