import pydantic as p
import typing as t
from fastapi import Depends
from ...constants.mongo import CollectionName
from ...common.models import StudentModel
from ...dependencies import MongoDbDep, LoggerDep
from ...interfaces.base_component import IBaseComponent

IGetStudents = IBaseComponent[None, "GetStudents.Response"]


class GetStudents(IGetStudents):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.STUDENTS)
        self._logger = logger

    class Response(p.BaseModel):
        students: list[StudentModel] = []

    async def aexecute(self, _=None) -> "Response":
        self._logger.info("Fetching all students from the database.")
        cursor = self._collection.find({})
        students = [StudentModel(**student) for student in cursor]
        return self.Response(students=students)


GetStudentsDep = t.Annotated[GetStudents, Depends(GetStudents)]
