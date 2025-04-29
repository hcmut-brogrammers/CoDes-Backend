from uuid import UUID

from fastapi import APIRouter, status

from ...components.design_projects import (
    CreateProjectDep,
    DeleteProjectByIdDep,
    GetProjectsByOrganizationIdDep,
    UpdateProjectDep,
)
from ...components.switch_organization import SwitchOrganization, SwitchOrganizationDep
from ...constants.router import ApiPath

router = APIRouter(
    prefix=ApiPath.PROJECTS,
    tags=["projects"],
)


@router.get(
    "",
    response_model=GetProjectsByOrganizationIdDep.Response,
    response_description="List of projects",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_projects_by_organization_id(get_projects_by_organization_id: GetProjectsByOrganizationIdDep):
    return await get_projects_by_organization_id.aexecute()


@router.post(
    "",
    response_model=CreateProjectDep.Response,
    response_description="Project created",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(create_project: CreateProjectDep, request: CreateProjectDep.Request):
    return await create_project.aexecute(request)


@router.put(
    "/{project_id}",
    response_model=UpdateProjectDep.Response,
    response_description="Project updated",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def update_project(update_project: UpdateProjectDep, project_id: UUID, request: UpdateProjectDep.HttpRequest):
    return await update_project.aexecute(UpdateProjectDep.Request(project_id=project_id, **request.model_dump()))


@router.delete(
    "/{project_id}",
    response_model=DeleteProjectByIdDep.Response,
    response_description="Project deleted",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def delete_organization_by_id(deleted_organization: DeleteProjectByIdDep, project_id: UUID):
    return await deleted_organization.aexecute(DeleteProjectByIdDep.Request(project_id=project_id))
