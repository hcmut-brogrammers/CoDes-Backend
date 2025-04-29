import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import ProjectModel
from ...common.models.user import UserRole
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import BadRequestError, InternalServerError
from ...interfaces.base_component import IBaseComponent
from ...utils.logger import execute_service_method

ICreateProject = IBaseComponent["CreateProject.Request", "CreateProject.Response"]

DEFAULT_THUMBNAIL_URL = p.HttpUrl(
    "https://s3-figma-hubfile-images-production.figma.com/hub/file/carousel/img/238a7016bbc93dbc4aa491c39f0f9c4595f31dee"
)


class CreateProject(ICreateProject):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._project_collection = db.get_collection(CollectionName.PROJECTS)
        self._logger = logger
        self._user_context = user_context

    class Request(p.BaseModel):
        name: str

    class Response(p.BaseModel):
        created_project: ProjectModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        user_id = self._user_context.user_id
        organization_id = self._user_context.organization_id

        # check if the user is the owner of the organization
        if self._user_context.role != UserRole.OrganizationAdmin:
            self._logger.error(f"User {user_id} is not the owner of the organization {organization_id}")
            raise BadRequestError("User is not the owner of the organization")

        # process create organization
        project = ProjectModel(
            name=request.name,
            thumbnail_url=str(DEFAULT_THUMBNAIL_URL),
            owner_id=user_id,
            organization_id=organization_id,
        )
        project_data = project.model_dump(by_alias=True)
        inserted_project = self._project_collection.insert_one(project_data)

        # process response
        created_project = self._project_collection.find_one({"_id": inserted_project.inserted_id})
        if not created_project:
            self._logger.error(
                f"Insert project data with id {inserted_project.inserted_id} successfully, but unable to find the created project"
            )
            raise InternalServerError("Insert project data successfully, but unable to find the created project")

        created_project = ProjectModel(**created_project)
        return self.Response(created_project=created_project)


CreateProjectDep = t.Annotated[CreateProject, Depends()]
