from enum import Enum

import pydantic as p

from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete


class UserRole(str, Enum):
    OrganizationAdmin = "OrganizationAdmin"
    OrganizationMember = "OrganizationMember"


class UserModel(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete):
    username: str = p.Field(alias="username")
    email: str = p.Field(alias="email")
    hashed_password: str = p.Field(alias="hashed_password")
    role: UserRole = p.Field(alias="role", default=UserRole.OrganizationMember)
