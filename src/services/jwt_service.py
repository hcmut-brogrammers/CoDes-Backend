import typing as t
from datetime import datetime, timedelta
from uuid import UUID

import jwt
import pydantic as p
from fastapi import Depends
from passlib.context import CryptContext

from ..common.auth import TokenData
from ..common.models import UserModel, UserRole
from ..dependencies import LoggerDep, SettingsDep
from ..utils.common import get_utc_now

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JwtService:
    def __init__(self, settings: SettingsDep, logger: LoggerDep) -> None:
        self._settings = settings
        self._logger = logger

    def encode_jwt_token(self, token_data: TokenData) -> str:
        jwt_token = jwt.encode(token_data.model_dump(mode="json"), self._settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
        return jwt_token

    def decode_jwt_token(self, token: str, verify_exp: bool = True) -> TokenData:
        try:
            payload = jwt.decode(
                token, self._settings.JWT_SECRET_KEY, algorithms=ALGORITHM, options={"verify_exp": verify_exp}
            )
            validated_token_data = TokenData.model_validate(payload)
            return validated_token_data
        except jwt.ExpiredSignatureError as e:
            self._logger.error("JWT token has expired.")
            raise ValueError("JWT token has expired.") from e
        except p.ValidationError as e:
            self._logger.error("Invalid JWT token payload.")
            raise ValueError("Invalid JWT token payload.") from e
        except jwt.PyJWTError as e:
            self._logger.error(f"Error while decoding JWT token: {e}.")
            raise ValueError("Error while decoing JWT token.") from e
        except Exception as e:
            self._logger.error(f"Invalid JWT token: {e}.")
            raise ValueError("Invalid JWT token.") from e

    def hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_user_token_data(self, user: UserModel, user_role: UserRole, organization_id: UUID) -> TokenData:
        token_data = TokenData(
            user_id=user.id,
            username=user.username,
            email=user.email,
            role=user_role,
            organization_id=organization_id,
            sub=user.username,
            exp=int(self._get_access_token_expires().timestamp()),
        )

        return token_data

    def _get_access_token_expires(self) -> datetime:
        access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        return get_utc_now() + access_token_expires


JwtServiceDep = t.Annotated[JwtService, Depends()]
