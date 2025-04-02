from datetime import datetime, timezone
from uuid import UUID

from ...utils.common import generate_uuid, get_utc_now


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
