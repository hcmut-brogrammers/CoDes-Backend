import typing as t
from datetime import datetime, timezone
from uuid import UUID, uuid4


def get_utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def generate_uuid() -> UUID:
    return uuid4()


def find[T](elements: list[T], fn: t.Callable[[T], bool]) -> t.Optional[T]:
    for element in elements:
        if fn(element):
            return element
    return None
