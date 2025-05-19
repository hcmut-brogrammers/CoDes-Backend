import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import DesignProjectModel, PyObjectUUID
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import BadRequestError
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method
from .create_design_project import CreateDesignProjectDep
from .get_design_project_by_id import GetDesignProjectByIdDep

IDuplicateDesignProject = IBaseComponent["DuplicateDesignProject.Request", "DuplicateDesignProject.Response"]


class DuplicateDesignProject(IDuplicateDesignProject):
    def __init__(
        self,
        db: MongoDbDep,
        logger: LoggerDep,
        user_context: UserContextDep,
        create_design_project: CreateDesignProjectDep,
        get_design_project_by_id: GetDesignProjectByIdDep,
    ) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context
        self._create_design_project = create_design_project
        self._get_design_project_by_id = get_design_project_by_id

    class Request(p.BaseModel):
        project_id: PyObjectUUID

    class Response(p.BaseModel):
        duplicated_project: DesignProjectModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        organization_id = self._user_context.organization_id

        get_design_project_by_id_request = self._get_design_project_by_id.Request(
            project_id=request.project_id,
        )
        get_design_project_by_id_response = await self._get_design_project_by_id.aexecute(
            get_design_project_by_id_request
        )
        design_project = get_design_project_by_id_response.design_project

        if design_project.organization_id != organization_id:
            self._logger.error(f"User have no permission to duplicate the project {request.project_id}.")
            raise BadRequestError(f"User have no permission to duplicate the project.")

        create_design_project_request = self._create_design_project.Request(
            name=self.make_copy_project_name(design_project.name),
            thumbnail_url=design_project.thumbnail_url,
            elements=design_project.elements,
        )
        create_design_project_response = await self._create_design_project.aexecute(create_design_project_request)
        created_project = create_design_project_response.created_project

        return self.Response(duplicated_project=created_project)

    def make_copy_project_name(self, project_name: str) -> str:
        return f"Copy of {project_name}"


DuplicateDesignProjectDep = t.Annotated[DuplicateDesignProject, Depends()]
