from fastapi import APIRouter, status

from ...common.models import PyObjectUUID
from ...components.design_projects import (
    CreateDesignProject,
    CreateDesignProjectDep,
    DeleteDesignProjectById,
    DeleteDesignProjectByIdDep,
    DuplicateDesignProject,
    DuplicateDesignProjectDep,
    GetDesignProjectById,
    GetDesignProjectByIdDep,
    GetDesignProjectsByOrganizationId,
    GetDesignProjectsByOrganizationIdDep,
    UpdateDesignProject,
    UpdateDesignProjectDep,
)
from ...constants.router import ApiPath
from .elements import router as elements_router

router = APIRouter(
    prefix=ApiPath.DESIGN_PROJECTS,
    tags=["design-projects"],
)


@router.get(
    "",
    response_model=GetDesignProjectsByOrganizationId.Response,
    response_description="List of design projects in the current organization",
    response_model_by_alias=False,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def get_design_projects_by_organization_id(
    get_design_projects_by_organization_id: GetDesignProjectsByOrganizationIdDep,
):
    return await get_design_projects_by_organization_id.aexecute()


@router.get(
    "/{project_id}",
    response_model=GetDesignProjectById.Response,
    response_description="Get design project by id",
    response_model_by_alias=False,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def get_design_project_by_id(get_design_project_by_id: GetDesignProjectByIdDep, project_id: PyObjectUUID):
    return await get_design_project_by_id.aexecute(GetDesignProjectById.Request(project_id=project_id))


@router.post(
    "",
    response_model=CreateDesignProject.Response,
    response_description="Project created",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_design_project(create_design_project: CreateDesignProjectDep, request: CreateDesignProject.Request):
    return await create_design_project.aexecute(request)


@router.put(
    "/{project_id}",
    response_model=UpdateDesignProject.Response,
    response_description="Project updated",
    response_model_by_alias=False,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def update_design_project_by_id(
    update_design_project_by_id: UpdateDesignProjectDep,
    project_id: PyObjectUUID,
    request: UpdateDesignProject.HttpRequest,
):
    return await update_design_project_by_id.aexecute(
        UpdateDesignProject.Request(project_id=project_id, **request.model_dump())
    )


@router.post(
    "/{project_id}/duplicate",
    response_model=DuplicateDesignProject.Response,
    response_description="Project duplicated",
    response_model_by_alias=False,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def duplicate_design_project_by_id(
    update_design_project_by_id: DuplicateDesignProjectDep,
    project_id: PyObjectUUID,
):
    return await update_design_project_by_id.aexecute(DuplicateDesignProject.Request(project_id=project_id))


@router.delete(
    "/{project_id}",
    response_model=DeleteDesignProjectById.Response,
    response_description="Project deleted",
    response_model_by_alias=False,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def delete_design_project_by_id(
    delete_design_project_by_id: DeleteDesignProjectByIdDep, project_id: PyObjectUUID
):
    return await delete_design_project_by_id.aexecute(DeleteDesignProjectById.Request(project_id=project_id))


router.include_router(elements_router)
