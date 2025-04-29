import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.models import OrganizationModel
from ...common.models.project import DesignProjectModel
from ...common.models.user import UserRole
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import BadRequestError, NotFoundError
from ...interfaces.base_component import IBaseComponent
from ...utils.common import get_utc_now
from ...utils.logger import execute_service_method

IDeleteDesignProjectById = IBaseComponent["DeleteDesignProjectById.Request", "DeleteDesignProjectById.Response"]


class DeleteDesignProjectById(IDeleteDesignProjectById):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context

    class Request(p.BaseModel):
        project_id: UUID

    class Response(p.BaseModel):
        deleted_project: DesignProjectModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        user_id = self._user_context.user_id
        organization_id = self._user_context.organization_id

        # check if the user is the owner of the organization
        if self._user_context.role != UserRole.OrganizationAdmin:
            self._logger.error(f"User {user_id} is not the owner of the organization {organization_id}")
            raise BadRequestError("User is not the owner of the organization")

        # before update condition check
        filter = {"_id": request.project_id}
        project_data = self._collection.find_one(filter)

        if project_data is None:
            log_message = f"Project with id {request.project_id} not found."
            error_message = f"Project not found."
            self._logger.error(log_message)
            raise NotFoundError(error_message)

        # prepare project instance
        deleted_project = DesignProjectModel(**project_data).model_copy()

        if deleted_project.owner_id != user_id:
            log_message = f"User {user_id} is not the owner of the project {request.project_id}."
            error_message = f"Project not found."
            self._logger.error(log_message)
            raise NotFoundError(error_message)

        if deleted_project.organization_id != organization_id:
            log_message = f"Organization {organization_id} does not have the project {request.project_id}."
            error_message = f"Project not found."
            self._logger.error(log_message)
            raise NotFoundError(error_message)

        # process update
        deleted_project.is_deleted = True
        deleted_project.deleted_at = get_utc_now()

        self._collection.update_one({"_id": deleted_project.id}, {"$set": deleted_project.model_dump(exclude={"id"})})

        # process response
        return self.Response(deleted_project=deleted_project)


DeleteDesignProjectByIdDep = t.Annotated[DeleteDesignProjectById, Depends()]
