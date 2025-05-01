from uuid import UUID

from fastapi import APIRouter, status

from src.components.design_projects.design_entities.shapes.create_shape import CreateShapeDep
from src.constants.router import ApiPath

router = APIRouter(
    tags=["shapes"],
)


@router.post(
    "/{project_id}" + ApiPath.SHAPES,
    response_model=CreateShapeDep.Response,
    response_model_exclude_none=True,
    response_description="create shape in a project",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def create_shape(create_shape: CreateShapeDep, project_id: UUID, request: CreateShapeDep.HttpRequest):
    return await create_shape.aexecute(CreateShapeDep.Request(project_id=project_id, **request.model_dump()))
