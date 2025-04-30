from uuid import UUID

from fastapi import APIRouter, status

from ...components.design_projects import (
    CreateDesignProjectDep,
    DeleteDesignProjectByIdDep,
    GetDesignProjectsByOrganizationIdDep,
    UpdateDesignProjectDep,
)
from ...components.design_projects.design_entities.nodes.create_node import CreateNodeDep
from ...components.design_projects.design_entities.shapes.create_shape import CreateShapeDep
from ...constants.router import ApiPath

router = APIRouter(
    prefix=ApiPath.DESIGN_PROJECTS,
    tags=["design-projects"],
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


# [?] method: put or post?
@router.post(
    "/{project_id}" + ApiPath.NODES,
    response_model=CreateNodeDep.Response,
    response_description="create node in a project",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def create_node(create_node: CreateNodeDep, project_id: UUID, request: CreateNodeDep.HttpRequest):
    return await create_node.aexecute(CreateNodeDep.Request(project_id=project_id, **request.model_dump()))


@router.post(
    "/{project_id}" + ApiPath.SHAPES,
    response_model=CreateShapeDep.Response,
    response_description="create shape in a project",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def create_shape(create_shape: CreateShapeDep, project_id: UUID, request: CreateShapeDep.HttpRequest):
    return await create_shape.aexecute(CreateShapeDep.Request(project_id=project_id, **request.model_dump()))
