import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import DesignProjectModel, PyObjectUUID, UserRole
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import BadRequestError, NotFoundError
from ...interfaces import IBaseComponent
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method

IUpdateDesignProject = IBaseComponent["UpdateDesignProject.Request", "UpdateDesignProject.Response"]


class UpdateDesignProject(IUpdateDesignProject):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context

    class HttpRequest(p.BaseModel):
        name: str | None = None
        thumbnail_url: p.HttpUrl | None = None

    class Request(HttpRequest, p.BaseModel):
        project_id: PyObjectUUID

    class Response(p.BaseModel):
        updated_project: DesignProjectModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        user_id = self._user_context.user_id
        organization_id = self._user_context.organization_id

        if self._user_context.role != UserRole.OrganizationAdmin:
            self._logger.error(f"User {user_id} is not the owner of the organization {organization_id}")
            raise BadRequestError("User is not the owner of the organization")

        update_data = request.model_dump(exclude={"project_id"}, exclude_none=True)

        if not update_data:
            error_message = f"No fields to update for project id {request.project_id}."
            self._logger.info(error_message)
            raise BadRequestError(error_message)

        filter = {"_id": request.project_id}
        project_data = self._collection.find_one(filter)

        if project_data is None:
            log_message = f"Project with id {request.project_id} not found."
            error_message = f"Project not found."
            self._logger.error(log_message)
            raise NotFoundError(error_message)

        updated_project = DesignProjectModel(**project_data).model_copy()

        if updated_project.organization_id != organization_id:
            log_message = f"User have no permission to update the project {request.project_id}."
            error_message = f"User have no permission to update the project."
            self._logger.error(log_message)
            raise BadRequestError(error_message)

        if updated_project.owner_id != user_id:
            log_message = f"User {user_id} is not the owner of the project {request.project_id}."
            error_message = f"Project not found."
            self._logger.error(log_message)
            raise NotFoundError(error_message)

        if updated_project.organization_id != organization_id:
            log_message = f"Organization {organization_id} does not have the project {request.project_id}."
            error_message = f"Project not found."
            self._logger.error(log_message)
            raise NotFoundError(error_message)

        if request.name:
            updated_project.name = request.name
        if request.thumbnail_url:
            updated_project.thumbnail_url = str(request.thumbnail_url)
        updated_project.updated_at = get_utc_now()

        self._collection.update_one({"_id": updated_project.id}, {"$set": updated_project.model_dump(exclude={"id"})})

        return self.Response(updated_project=updated_project)


UpdateDesignProjectDep = t.Annotated[UpdateDesignProject, Depends()]
