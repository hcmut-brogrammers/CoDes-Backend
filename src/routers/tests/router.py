from fastapi import APIRouter

from ...constants.router import ApiPath
from . import students

router = APIRouter(
    prefix=ApiPath.TESTS,
    tags=["tests"],
)

router.include_router(students.router)
