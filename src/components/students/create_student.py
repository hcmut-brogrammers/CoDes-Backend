import pydantic as p
import typing as t
from fastapi import Depends
from ...constants.mongo import CollectionName
from ...common.models import StudentModel
from ...dependencies import MongoDbDep, LoggerDep
from ...interfaces import IBaseComponent

ICreateStudent = IBaseComponent["CreateStudent.Request", "CreateStudent.Response"]


class CreateStudent(ICreateStudent):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.STUDENTS)
        self._logger = logger

    class Request(StudentModel, p.BaseModel):
        pass

    class Response(p.BaseModel):
        student: StudentModel | None = None

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info("Creating a new student in the database.")
        new_student = self._collection.insert_one(
            request.model_dump(by_alias=True, exclude={"id"})
        )
        created_student = self._collection.find_one({"_id": new_student.inserted_id})
        if not created_student:
            return self.Response()

        return self.Response(student=created_student)


CreateStudentDep = t.Annotated[CreateStudent, Depends(CreateStudent)]
