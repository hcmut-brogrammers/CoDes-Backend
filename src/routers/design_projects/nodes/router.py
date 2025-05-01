from uuid import UUID

from fastapi import APIRouter, status

from src.components.design_projects.design_entities.nodes.create_node import CreateNodeDep
from src.components.design_projects.design_entities.nodes.delete_node import DeleteNodeDep
from src.components.design_projects.design_entities.nodes.get_nodes import GetNodesDep
from src.components.design_projects.design_entities.nodes.update_node import UpdateNode, UpdateNodeDep
from src.constants.router import ApiPath

router = APIRouter(
    tags=["nodes"],
)


@router.post(
    "/{project_id}" + ApiPath.NODES,
    response_model=CreateNodeDep.Response,
    response_model_exclude_none=True,
    response_description="create node in a project",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def create_node(create_node: CreateNodeDep, project_id: UUID, request: CreateNodeDep.HttpRequest):
    return await create_node.aexecute(CreateNodeDep.Request(project_id=project_id, **request.model_dump()))


@router.get(
    "/{project_id}" + ApiPath.NODES,
    response_model=GetNodesDep.Response,
    response_model_exclude_none=True,
    response_description="create node in a project",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_nodes(get_nodes: GetNodesDep, project_id: UUID):
    return await get_nodes.aexecute(GetNodesDep.Request(project_id=project_id))


@router.put(
    "/{project_id}" + ApiPath.NODES,
    response_model=UpdateNodeDep.Response,
    response_model_exclude_none=True,
    response_description="update node in a project",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def update_node(update_node: UpdateNodeDep, project_id: UUID, request: UpdateNodeDep.HttpRequest):
    return await update_node.aexecute(UpdateNodeDep.Request(project_id=project_id, **request.model_dump()))


@router.delete(
    "/{project_id}" + ApiPath.NODES,
    response_model=UpdateNodeDep.Response,
    response_model_exclude_none=True,
    response_description="delete node in a project",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def delete_node(delete_node: DeleteNodeDep, project_id: UUID, request: DeleteNodeDep.HttpRequest):
    return await delete_node.aexecute(DeleteNodeDep.Request(project_id=project_id, **request.model_dump()))
