import typing as t

import pydantic as p
from fastapi import Depends
from pymongo.cursor import Cursor

from ...common.models import ProjectModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import InternalServerError
from ...interfaces.base_component import IBaseComponent
from ...utils.logger import execute_service_method

ICreateProject = IBaseComponent["CreateProject.Request", "CreateProject.Response"]


class CreateProject(ICreateProject):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._collection = db.get_collection(CollectionName.PROJECTS)
        self._logger = logger
        self._user_context = user_context

    class Request(p.BaseModel):
        name: str
        thumbnail_url: p.HttpUrl | None = None

    class Response(p.BaseModel):
        created_project: ProjectModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        # check if the owner already has a default organization
        filter = {
            "owner_id": self._user_context.user_id,
            "is_default": True,
        }
        organization_data = self._collection.find_one(filter)

        # process create organization
        organization = ProjectModel(
            name=request.name,
            thumbnail_url=str(request.thumbnail_url),
            owner_id=self._user_context.user_id,
            organization_id=self._user_context.organization_id,
        )
        organization_data = organization.model_dump(by_alias=True)
        inserted_organization = self._collection.insert_one(organization_data)
        created_organization = self._collection.find_one({"_id": inserted_organization.inserted_id})
        if not created_organization:
            self._logger.error(
                f"Insert organization data with id {inserted_organization.inserted_id} successfully, but unable to find the created organization"
            )
            raise InternalServerError(
                "Insert organization data successfully, but unable to find the created organization"
            )

        created_organization = ProjectModel(**created_organization)
        return self.Response(created_project=created_organization)


CreateProjectDep = t.Annotated[CreateProject, Depends()]
