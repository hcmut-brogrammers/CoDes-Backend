from fastapi import APIRouter, status

from ....components.students import CreateStudentDep, GetStudentsDep

router = APIRouter(
    prefix="/students",
    tags=["students"],
)


@router.get(
    "",
    response_model=GetStudentsDep.Response,
    response_description="List of students",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_students(get_students: GetStudentsDep):
    return await get_students.aexecute()


@router.post(
    "",
    response_model=CreateStudentDep.Response,
    response_description="Student created",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_student(create_student: CreateStudentDep, request: CreateStudentDep.Request):
    return await create_student.aexecute(request)
