import typing as t

import pydantic as p
from fastapi import Depends

from ....common.models import BaseElementModel, DesignProjectModel, ElementModel, PyObjectUUID
from ....constants.mongo import CollectionName
from ....dependencies import LoggerDep, MongoDbDep
from ....exceptions import BadRequestError
from ....interfaces import IBaseComponent
from ....utils.design_element import create_element
from ....utils.logger import execute_service_method

IBaseCreateElement = IBaseComponent["BaseCreateElement.Request", "BaseCreateElement.Response"]


class BaseCreateElement(IBaseCreateElement):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger

    class Request(p.BaseModel):
        design_project_id: PyObjectUUID
        organization_id: PyObjectUUID
        element: BaseElementModel

    class Response(p.BaseModel):
        created_element: ElementModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        design_project_id = request.design_project_id
        organization_id = request.organization_id

        design_project_data = self._collection.find_one({"_id": design_project_id})
        if not design_project_data:
            log_message = f"Design project with id {design_project_id} not found."
            error_message = f"Design project not found."
            self._logger.error(log_message)
            raise BadRequestError(error_message)

        design_project = DesignProjectModel(**design_project_data)
        if design_project.organization_id != organization_id:
            log_message = f"User have no permission to access the design project {design_project_id}."
            error_message = f"User have no permission to access the design project."
            self._logger.error(log_message)
            raise BadRequestError(error_message)

        element = create_element(request.element)
        self._collection.update_one(
            {"_id": design_project_id},
            {
                "$push": {
                    "elements": {
                        "$each": [element.model_dump(by_alias=True, exclude_none=True)],
                        "$position": 0,
                    }
                }
            },
        )
        return self.Response(created_element=element)


BaseCreateElementDep = t.Annotated[BaseCreateElement, Depends()]
