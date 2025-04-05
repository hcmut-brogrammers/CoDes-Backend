from uuid import UUID

import pydantic as p

from ...common.models import UserRole


class TokenData(p.BaseModel):
    user_id: UUID
    username: str
    email: str
    role: UserRole
    sub: str
    exp: int
