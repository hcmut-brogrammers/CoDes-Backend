import typing as t

import pydantic as p
from fastapi import Depends
from pymongo import UpdateOne

from ....common.models import BaseElementModel, ElementModel, PyObjectUUID
from ....constants.mongo import CollectionName
from ....dependencies import LoggerDep, MongoDbDep
from ....exceptions import BadRequestError
from ....interfaces import IBaseComponent
from ....utils.design_element import create_element
from ....utils.logger import execute_service_method

IBaseCreateBatchElements = IBaseComponent["BaseCreateBatchElements.Request", "BaseCreateBatchElements.Response"]


class BaseCreateBatchElements(IBaseCreateBatchElements):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger

    class Request(p.BaseModel):
        base_elements: list[BaseElementModel]
        organization_id: PyObjectUUID
        project_id: PyObjectUUID

    class Response(p.BaseModel):
        created_elements: list[ElementModel]

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        project_id = request.project_id
        organization_id = request.organization_id
        # TODO: refactor to a separate component
        is_project_exist = self._collection.count_documents(
            {"_id": project_id, "organization_id": organization_id}, limit=1
        )
        if is_project_exist < 1:
            self._logger.error(f"Project with id {project_id} not found.")
            raise BadRequestError(f"Project with id {project_id} not found.")

        elements: list[ElementModel] = []
        bulk_operations = []
        for base_element in request.base_elements:
            element = create_element(base_element)
            element_data = element.model_dump(by_alias=True, exclude_none=True)
            bulk_operations.append(
                UpdateOne(
                    {"_id": project_id},
                    {
                        "$push": {
                            "elements": {
                                "$each": [element_data],
                                "$position": 0,
                            }
                        }
                    },
                )
            )
            elements.append(element)

        if not len(bulk_operations):
            self._logger.info("No update operations provided.")
            return self.Response(created_elements=[])

        # process bulk update operations
        try:
            bulk_write_result = self._collection.bulk_write(bulk_operations, ordered=False)
            # log bulk result data
            self._logger.info(bulk_write_result.bulk_api_result)
        except Exception as e:
            self._logger.error(f"Bulk update failed: {e}")
            return self.Response(created_elements=[])

        return self.Response(created_elements=elements)


BaseCreateBatchElementsDep = t.Annotated[BaseCreateBatchElements, Depends()]
