import typing as t

import pydantic as p
from fastapi import Depends

from ....common.models import ElementModel, PyObjectUUID
from ....constants.mongo import CollectionName
from ....dependencies import LoggerDep, MongoDbDep
from ....exceptions import BadRequestError
from ....interfaces import IBaseComponent
from ....utils.common import get_utc_now
from ....utils.logger import execute_service_method

IBaseUpdateElement = IBaseComponent["BaseUpdateElement.Request", "BaseUpdateElement.Response | None"]


class BaseUpdateElement(IBaseUpdateElement):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger

    class Request(p.BaseModel):
        # TODO: element should be a base element without element's metadata
        element: ElementModel
        organization_id: PyObjectUUID
        project_id: PyObjectUUID
        element_id: PyObjectUUID

    class Response(p.BaseModel):
        updated_element: ElementModel

    async def aexecute(self, request: "Request") -> "Response | None":
        self._logger.info(execute_service_method(self))

        element = request.element
        project_id = request.project_id
        organization_id = request.organization_id
        element_id = request.element_id

        is_project_exist = self._collection.count_documents(
            {"_id": project_id, "organization_id": organization_id}, limit=1
        )
        if is_project_exist < 1:
            self._logger.error(f"Project with id {project_id} not found.")
            raise BadRequestError(f"Project with id {project_id} not found.")

        updated_element = element.model_copy()
        updated_element.id = element_id
        updated_element.updated_at = get_utc_now()
        updated_element_data = updated_element.model_dump(exclude={"id"}, exclude_none=True)
        # TODO: find the matched element, update it and return the updated element
        update_one_result = self._collection.update_one(
            {"_id": project_id, "elements._id": element_id},
            {"$set": {"elements.$": {"_id": element_id, **updated_element_data}}},
        )

        if update_one_result.matched_count == 0:
            self._logger.error(f"Element with id {element_id} not found in project {project_id}.")
            return None

        if update_one_result.modified_count == 0:
            self._logger.error(f"Failed to modify element with id {element_id} in project {project_id}.")
            return None

        return self.Response(updated_element=updated_element)


BaseUpdateElementDep = t.Annotated[BaseUpdateElement, Depends()]
