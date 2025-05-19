import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import DesignProjectModel, PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import NotFoundError
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method

IGetDesignProjectById = IBaseComponent["GetDesignProjectById.Request", "GetDesignProjectById.Response"]


class GetDesignProjectById(IGetDesignProjectById):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger

    class Request(p.BaseModel):
        project_id: PyObjectUUID

    class Response(p.BaseModel):
        design_project: DesignProjectModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        filter = {"_id": request.project_id}
        project_data = self._collection.find_one(filter)
        if not project_data:
            self._logger.info(f"Project with id {request.project_id} not found.")
            raise NotFoundError(f"Project with id {request.project_id} not found.")

        design_project = DesignProjectModel(**project_data)
        return self.Response(design_project=design_project)


GetDesignProjectByIdDep = t.Annotated[GetDesignProjectById, Depends()]
