import typing as t

import pydantic as p
from fastapi import Depends

from ....common.models import DesignProjectModel, PyObjectUUID, ShapeElementModel
from ....constants.mongo import CollectionName
from ....dependencies import LoggerDep, MongoDbDep
from ....exceptions import BadRequestError
from ....interfaces import IBaseComponent
from ....utils.logger import execute_service_method

IBaseGetElements = IBaseComponent["BaseGetElements.Request", "BaseGetElements.Response"]


class BaseGetElements(IBaseGetElements):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger

    class Request(p.BaseModel):
        organization_id: PyObjectUUID
        project_id: PyObjectUUID

    class Response(p.BaseModel):
        elements: list[ShapeElementModel]

    async def aexecute(self, request: Request) -> "Response":
        self._logger.info(execute_service_method(self))
        project_id = request.project_id
        organization_id = request.organization_id

        current_project_data = self._collection.find_one({"_id": project_id})
        if not current_project_data:
            log_message = f"Project with id {project_id} not found."
            error_message = f"Project not found."
            self._logger.error(log_message)
            raise BadRequestError(error_message)

        current_project = DesignProjectModel(**current_project_data)
        if current_project.organization_id != organization_id:
            log_message = f"User have no permission to access the project {project_id}."
            error_message = f"User have no permission to access the project."
            self._logger.error(log_message)
            raise BadRequestError(error_message)

        elements = current_project.elements
        return self.Response(elements=elements)


BaseGetElementsDep = t.Annotated[BaseGetElements, Depends()]
