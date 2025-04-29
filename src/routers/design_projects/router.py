from uuid import UUID

from fastapi import APIRouter, status

from ...components.design_projects import (
    CreateDesignProjectDep,
    DeleteDesignProjectByIdDep,
    GetDesignProjectsByOrganizationIdDep,
    UpdateDesignProjectDep,
)
from ...constants.router import ApiPath

router = APIRouter(
    prefix=ApiPath.DESIGN_PROJECTS,
    tags=["design projects"],
)


@router.get(
    "",
    response_model=GetDesignProjectsByOrganizationIdDep.Response,
    response_description="List of design projects",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_design_projects_by_organization_id(
    get_design_projects_by_organization_id: GetDesignProjectsByOrganizationIdDep,
):
    return await get_design_projects_by_organization_id.aexecute()


@router.post(
    "",
    response_model=CreateDesignProjectDep.Response,
    response_description="Project created",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_design_project(create_design_project: CreateDesignProjectDep, request: CreateDesignProjectDep.Request):
    return await create_design_project.aexecute(request)


@router.put(
    "/{project_id}",
    response_model=UpdateDesignProjectDep.Response,
    response_description="Project updated",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def update_design_project_by_id(
    update_design_project_by_id: UpdateDesignProjectDep, project_id: UUID, request: UpdateDesignProjectDep.HttpRequest
):
    return await update_design_project_by_id.aexecute(
        UpdateDesignProjectDep.Request(project_id=project_id, **request.model_dump())
    )


@router.delete(
    "/{project_id}",
    response_model=DeleteDesignProjectByIdDep.Response,
    response_description="Project deleted",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def delete_design_project_by_id(delete_design_project_by_id: DeleteDesignProjectByIdDep, project_id: UUID):
    return await delete_design_project_by_id.aexecute(DeleteDesignProjectByIdDep.Request(project_id=project_id))
