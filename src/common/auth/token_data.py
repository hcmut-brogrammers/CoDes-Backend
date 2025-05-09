from uuid import UUID

import pydantic as p

from ...common.models import PyObjectUUID, UserRole


class TokenData(p.BaseModel):
    user_id: PyObjectUUID
    username: str
    email: str
    role: UserRole
    organization_id: PyObjectUUID
    sub: str
    exp: int
