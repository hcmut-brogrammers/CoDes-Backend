from enum import Enum
from typing import Optional

import pydantic as p

from .base import BaseModelWithDateTime, BaseModelWithId, BaseModelWithSoftDelete, PyObjectUUID


class CategoryModel(BaseModelWithId, BaseModelWithDateTime, BaseModelWithSoftDelete):
    name: str
    description: str
