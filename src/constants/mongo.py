from dataclasses import dataclass


@dataclass(frozen=True)
class CollectionName:
    STUDENTS: str = "students"
    USERS: str = "users"
    REFRESH_TOKENS: str = "refresh_tokens"
