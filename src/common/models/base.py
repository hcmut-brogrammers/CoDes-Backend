from datetime import datetime, timezone
from typing import Annotated
from urllib.parse import urlparse
from uuid import UUID

import pydantic as p
from pydantic.functional_validators import AfterValidator

from ...utils.common import generate_uuid, get_utc_now


def validate_uuid(value: UUID | str) -> UUID:
    if isinstance(value, UUID):
        return value

    try:
        return UUID(value)
    except ValueError:
        raise ValueError(f"{value} is not a valid UUID")


def validate_datetime(value: datetime | str) -> datetime:
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value


def is_http_url(v: str | None) -> str | None:
    if v is None:
        return v
    parsed = urlparse(v)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("avatar_url must be a valid HTTP or HTTPS URL")
    return v


PyObjectHttpUrlStr = Annotated[str, AfterValidator(is_http_url)]
PyObjectUUID = Annotated[UUID, p.BeforeValidator(validate_uuid)]
PyObjectDatetime = Annotated[datetime, p.BeforeValidator(validate_datetime)]


class BaseModelWithId(p.BaseModel):
    id: PyObjectUUID = p.Field(alias="_id", default_factory=generate_uuid)

    model_config = p.ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class BaseModelWithDateTime(p.BaseModel):
    created_at: PyObjectDatetime = p.Field(alias="created_at", default_factory=get_utc_now)
    updated_at: PyObjectDatetime = p.Field(alias="updated_at", default_factory=get_utc_now)

    model_config = p.ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class BaseModelWithSoftDelete(p.BaseModel):
    is_deleted: bool = p.Field(alias="is_deleted", default=False)
    deleted_at: PyObjectDatetime | None = p.Field(alias="deleted_at", default=None)

    model_config = p.ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
