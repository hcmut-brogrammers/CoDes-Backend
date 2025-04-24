from datetime import datetime, timezone
from uuid import UUID

import pytest

from ...utils.common import generate_uuid, get_utc_now, get_utc_shifted_from


class TestGetUtcNow:
    def test_get_utc_now(self):
        # Test that get_utc_now returns a datetime object with UTC timezone
        now = get_utc_now()
        assert isinstance(now, datetime)
        assert now.tzinfo == timezone.utc

    def test_get_utc_now_is_utc(self):
        # Test that the returned datetime is in UTC
        now = get_utc_now()
        assert now.tzinfo == timezone.utc


class TestGenerateUuid:
    def test_generate_uuid(self):
        # Test that generate_uuid returns a valid UUID object
        uuid = generate_uuid()
        assert isinstance(uuid, UUID)
        assert uuid.version == 4

    def test_generate_uuid_is_unique(self):
        # Test that two generated UUIDs are unique
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        assert uuid1 != uuid2


class TestGetUtcShiftedFrom:
    def test_get_utc_shifted_from(self):
        # Test that get_utc_shifted_from returns a datetime object with UTC timezone
        time_now = get_utc_now()
        get_time = get_utc_shifted_from(time_now, True, n_hours=2)
        assert isinstance(get_time, datetime)
        assert get_time.tzinfo == timezone.utc

    def test_get_utc_shifted_from_is_utc(self):
        # Test that the returned datetime is in UTC
        time_now = get_utc_now()
        get_time = get_utc_shifted_from(time_now, True, n_hours=2)
        assert get_time.tzinfo == timezone.utc

    def test_get_utc_shifted_from_with_earlier_time(self):
        # Test that the returned datetime is in UTC
        time_now = get_utc_now()
        get_time = get_utc_shifted_from(time_now, False, n_hours=2)
        assert get_time < time_now

    def test_get_utc_shifted_from_with_later_time(self):
        # Test that the returned datetime is in UTC
        time_now = get_utc_now()
        get_time = get_utc_shifted_from(time_now, True, n_hours=2)
        assert get_time > time_now

    def test_get_utc_shifted_from_with_non_UTC_base_time_should_raise(self):
        # Given a naive datetime (not timezone-aware)
        naive_time = datetime.now()  # No tzinfo

        # When/Then: Expect a ValueError because the datetime is not UTC-aware
        with pytest.raises(ValueError, match="base_time must be timezone-aware and in UTC"):
            get_utc_shifted_from(naive_time, True, n_hours=2)
