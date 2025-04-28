from uuid import UUID

import pydantic as p

from ...common.models import UserRole


class TokenData(p.BaseModel):
    user_id: UUID
    username: str
    email: str
    role: UserRole
    organization_id: UUID
    sub: str
    exp: int
