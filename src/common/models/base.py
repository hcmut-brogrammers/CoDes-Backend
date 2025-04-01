from typing import Annotated

import pydantic as p

PyObjectId = Annotated[str, p.BeforeValidator(str)]


class BaseModel(p.BaseModel):
    id: PyObjectId | None = p.Field(alias="_id", default=None)

    model_config = p.ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
