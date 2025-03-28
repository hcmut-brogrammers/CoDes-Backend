import pydantic as p
import typing as t
from fastapi import Depends
from ...constants.mongo import CollectionName
from ...common.models import StudentModel
from ...dependencies import MongoDbDep, LoggerDep


class GetStudents:
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.STUDENTS)
        self._logger = logger

    class Response(p.BaseModel):
        students: list[StudentModel] = []

    async def execute_async(self) -> "Response":
        self._logger.info("Fetching all students from the database.")
        cursor = self._collection.find({})
        students = [StudentModel(**student) for student in cursor]
        return self.Response(students=students)


GetStudentsDep = t.Annotated[GetStudents, Depends(GetStudents)]
