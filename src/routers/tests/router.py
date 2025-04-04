from fastapi import APIRouter

from . import students

router = APIRouter(
    prefix="/tests",
    tags=["tests"],
)

router.include_router(students.router)
