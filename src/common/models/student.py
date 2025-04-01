import pydantic as p

from .base import BaseModel


class StudentModel(BaseModel):
    name: str = p.Field(...)
    email: p.EmailStr = p.Field(...)
    course: str = p.Field(...)
    gpa: float = p.Field(..., le=4.0)
