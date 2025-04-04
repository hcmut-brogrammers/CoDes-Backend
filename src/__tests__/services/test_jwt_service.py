from datetime import timedelta
from unittest.mock import Mock
from uuid import uuid4

import jwt
import pytest
from passlib.context import CryptContext

from ...common.models import UserModel, UserRole
from ...services.jwt_service import JwtService, TokenData
from ...utils.common import get_utc_now


@pytest.fixture
def jwt_service() -> JwtService:
    mock_settings = Mock(JWT_SECRET_KEY="test_secret_key")
    mock_logger = Mock()
    return JwtService(settings=mock_settings, logger=mock_logger)


def test_encode_jwt_token(jwt_service) -> None:
    token_data = TokenData(
        user_id=uuid4(),
        username="testuser",
        email="testuser@example.com",
        role=UserRole.OrganizationAdmin,
        sub="testuser",
        exp=int((get_utc_now() + timedelta(hours=1)).timestamp()),
    )
    token = jwt_service.encode_jwt_token(token_data)
    decoded_payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
    assert decoded_payload["username"] == "testuser"
    assert decoded_payload["email"] == "testuser@example.com"


def test_decode_jwt_token(jwt_service) -> None:
    payload = {
        "user_id": str(uuid4()),
        "username": "testuser",
        "email": "testuser@example.com",
        "role": UserRole.OrganizationAdmin,
        "sub": "testuser",
        "exp": int((get_utc_now() + timedelta(hours=1)).timestamp()),
    }
    token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
    token_data = jwt_service.decode_jwt_token(token)
    assert token_data.username == "testuser"
    assert token_data.email == "testuser@example.com"


def test_decode_jwt_token_invalid(jwt_service) -> None:
    invalid_token = "invalid.token.value"
    with pytest.raises(ValueError, match="Cannot parse access token"):
        jwt_service.decode_jwt_token(invalid_token)


def test_hash_and_verify_password(jwt_service) -> None:
    password = "securepassword"
    hashed_password = jwt_service.hash(password)
    assert CryptContext(schemes=["bcrypt"]).verify(password, hashed_password)
    assert jwt_service.verify_password(password, hashed_password) is True
    assert jwt_service.verify_password("wrongpassword", hashed_password) is False


def test_create_user_token_data(jwt_service) -> None:
    user = UserModel(
        _id=uuid4(),
        username="testuser",
        email="testuser@example.com",
        role=UserRole.OrganizationAdmin,
        hashed_password="hashed_password",
    )
    token_data = jwt_service.create_user_token_data(user)
    assert token_data.username == "testuser"
    assert token_data.email == "testuser@example.com"
    assert token_data.role == UserRole.OrganizationAdmin


def test_hash_method(jwt_service) -> None:
    password = "securepassword"
    hashed_password = jwt_service.hash(password)
    assert hashed_password != password  # Ensure the password is hashed
    assert CryptContext(schemes=["bcrypt"]).verify(password, hashed_password)  # Verify the hash


def test_hash_method_different_hashes_for_same_input(jwt_service) -> None:
    password = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjlkYTdjMzUtNzJhOC00MzY3LWE4YjctYzc0NWZhOWFmNTdlIiwidXNlcm5hbWUiOiJ0aWVuMSIsImVtYWlsIjoidGllbjRAZ21haWwuY29tIiwicm9sZSI6Ik9yZ2FuaXphdGlvbkFkbWluIiwic3ViIjoidGllbjEiLCJleHAiOjE3NDM3NzMxODJ9.Q_Nvr117Lkgd5vKljx0LqcqeWGkiQyug0iYGbp5cxeA"
    hashed_password_1 = jwt_service.hash(password)
    hashed_password_2 = jwt_service.hash(password)
    assert hashed_password_1 != hashed_password_2  # Ensure hashes are different
