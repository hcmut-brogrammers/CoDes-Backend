from datetime import datetime, timezone
from uuid import UUID, uuid4


def get_utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def generate_uuid() -> UUID:
    return uuid4()
