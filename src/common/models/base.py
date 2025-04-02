from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

import pydantic as p

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
