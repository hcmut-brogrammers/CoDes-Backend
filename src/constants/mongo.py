from dataclasses import dataclass


@dataclass(frozen=True)
class CollectionName:
    STUDENTS: str = "students"
    USERS: str = "users"
