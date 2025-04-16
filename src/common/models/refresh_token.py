from datetime import datetime

import pydantic as p

from .base import BaseModelWithId, BaseModelWithSoftDelete


# class RefreshTokenModel(BaseModelWithId, BaseModelWithSoftDelete):
class RefreshTokenModel(BaseModelWithId):
    hashed_access_token: str = p.Field(alias="hashed_access_token")
    expired_at: datetime = p.Field(alias="expired_at")
    revoked_at: datetime | None = p.Field(alias="revoked_at", default=None)
