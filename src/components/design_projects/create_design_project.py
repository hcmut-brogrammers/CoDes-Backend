import typing as t

import pydantic as p
from fastapi import Depends

from ...common.models import DesignProjectModel, ElementModel, PyObjectHttpUrlStr, UserRole
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import BadRequestError, InternalServerError
from ...interfaces import IBaseComponent
from ...utils.logger import execute_service_method

ICreateDesignProject = IBaseComponent["CreateDesignProject.Request", "CreateDesignProject.Response"]

DEFAULT_THUMBNAIL_URL = p.HttpUrl(
    "https://s3-figma-hubfile-images-production.figma.com/hub/file/carousel/img/238a7016bbc93dbc4aa491c39f0f9c4595f31dee"
)


class CreateDesignProject(ICreateDesignProject):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.DESIGN_PROJECTS)
        self._logger = logger
        self._user_context = user_context

    class Request(p.BaseModel):
        name: str
        thumbnail_url: PyObjectHttpUrlStr | None = None
        elements: list[ElementModel] = []

    class Response(p.BaseModel):
        created_project: DesignProjectModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        user_id = self._user_context.user_id
        organization_id = self._user_context.organization_id

        if self._user_context.role != UserRole.OrganizationAdmin:
            self._logger.error(f"User {user_id} is not the owner of the organization {organization_id}")
            raise BadRequestError("User is not the owner of the organization")

        project = DesignProjectModel(
            name=request.name,
            thumbnail_url=request.thumbnail_url or str(DEFAULT_THUMBNAIL_URL),
            owner_id=user_id,
            organization_id=organization_id,
            elements=request.elements,
        )
        project_data = project.model_dump(by_alias=True)
        insert_one_result = self._collection.insert_one(project_data)

        created_project = self._collection.find_one({"_id": insert_one_result.inserted_id})
        if not created_project:
            self._logger.error(
                f"Insert project data with id {insert_one_result.inserted_id} successfully, but unable to find the created project"
            )
            raise InternalServerError("Insert project data successfully, but unable to find the created project")

        created_project = DesignProjectModel(**created_project)
        return self.Response(created_project=created_project)


CreateDesignProjectDep = t.Annotated[CreateDesignProject, Depends()]
