from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4


def get_utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def generate_uuid() -> UUID:
    return uuid4()


def get_utc_shifted_from(
    base_time: datetime, is_later: bool, n_days: int = 0, n_hours: int = 0, n_minutes: int = 0, n_seconds: int = 0
) -> datetime:
    """
    Shift a given UTC datetime by a specified amount of time.

    Args:
        base_time (datetime): The base UTC datetime to shift. Must be timezone-aware in UTC.
        is_later (bool): True to move forward in time, False to move backward.
        n_days (int): Days to shift.
        n_hours (int): Hours to shift.
        n_minutes (int): Minutes to shift.
        n_seconds (int): Seconds to shift.

    Returns:
        datetime: The shifted UTC datetime.

    Raises:
        ValueError: If base_time is not timezone-aware in UTC.

    Example:
        >>> from datetime import datetime, timezone
        >>> base = datetime.now(timezone.utc)
        >>> get_utc_shifted_from(base, True, n_days=1, n_hours=2)
        datetime.datetime(2025, 4, 25, 14, 30, tzinfo=datetime.timezone.utc)
    """
    if base_time.tzinfo != timezone.utc:
        raise ValueError("base_time must be timezone-aware and in UTC")

    delta = timedelta(days=n_days, hours=n_hours, minutes=n_minutes, seconds=n_seconds)
    return base_time + delta if is_later else base_time - delta
