import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.models.project import ProjectModel
from ...common.models.user import UserRole
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import BadRequestError, NotFoundError
from ...interfaces.base_component import IBaseComponent
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method

IUpdateProject = IBaseComponent["UpdateProject.Request", "UpdateProject.Response"]


class UpdateProject(IUpdateProject):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.PROJECTS)
        self._logger = logger
        self._user_context = user_context

    class HttpRequest(p.BaseModel):
        name: str | None = None
        thumbnail_url: p.HttpUrl | None = None

    class Request(HttpRequest, p.BaseModel):
        project_id: UUID

    class Response(p.BaseModel):
        updated_organization: ProjectModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        user_id = self._user_context.user_id
        organization_id = self._user_context.organization_id

        # check if the user is the owner of the organization
        if self._user_context.role != UserRole.OrganizationAdmin:
            self._logger.error(f"User {user_id} is not the owner of the organization {organization_id}")
            raise BadRequestError("User is not the owner of the organization")

        update_data = request.model_dump(exclude={"project_id"}, exclude_none=True)

        # handle the case when no fields are provided for update
        if not update_data:
            error_message = f"No fields to update for project id {request.project_id}."
            self._logger.info(error_message)
            raise BadRequestError(error_message)

        # before update condition check
        filter = {"_id": request.project_id}
        current_project = self._collection.find_one(filter)

        if current_project is None:
            log_message = f"Project with id {request.project_id} not found."
            error_message = f"Project not found."
            self._logger.error(log_message)
            raise NotFoundError(error_message)

        if current_project["owner_id"] is not user_id:
            log_message = f"User {user_id} is not the owner of the project {request.project_id}."
            error_message = f"Project not found."
            self._logger.error(log_message)
            raise NotFoundError(error_message)

        if current_project["organization_id"] is not organization_id:
            log_message = f"Organizaiotn {organization_id} does not have the project {request.project_id}."
            error_message = f"Project not found."
            self._logger.error(log_message)
            raise NotFoundError(error_message)

        # process update
        updated_project = ProjectModel(**current_project).model_copy()
        if request.name:
            updated_project.name = request.name
        if request.thumbnail_url:
            updated_project.thumbnail_url = str(request.thumbnail_url)
        updated_project.updated_at = get_utc_now()

        self._collection.update_one({"_id": updated_project.id}, {"$set": updated_project.model_dump(exclude={"id"})})

        # process response
        return self.Response(updated_organization=updated_project)


UpdateProjectDep = t.Annotated[UpdateProject, Depends()]
