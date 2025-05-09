from fastapi import APIRouter, status

from ....common.models import PyObjectUUID
from ....components.design_projects.elements import (
    CreateBatchElements,
    CreateBatchElementsDep,
    CreateElement,
    CreateElementDep,
    DeleteElement,
    DeleteElementDep,
    GetElements,
    GetElementsDep,
    UpdateElement,
    UpdateElementDep,
)
from ....constants.router import ApiPath

router = APIRouter(
    prefix="/{design_project_id}",
    tags=["elements"],
)


@router.post(
    ApiPath.ELEMENTS,
    response_model=CreateElement.Response,
    response_model_exclude_none=True,
    response_description="Element created in design project",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_element(
    design_project_id: PyObjectUUID, request: CreateElement.HttpRequest, create_element: CreateElementDep
):
    return await create_element.aexecute(
        CreateElement.Request(design_project_id=design_project_id, element=request.element)
    )


@router.post(
    f"{ApiPath.ELEMENTS}/batch",
    response_model=CreateBatchElements.Response,
    response_model_exclude_none=True,
    response_description="Elements batch created in design project",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_batch_elements(
    design_project_id: PyObjectUUID,
    request: CreateBatchElements.HttpRequest,
    create_batch_elements: CreateBatchElementsDep,
):
    return await create_batch_elements.aexecute(
        CreateBatchElements.Request(
            project_id=design_project_id,
            elements=request.elements,
        )
    )


@router.get(
    ApiPath.ELEMENTS,
    response_model=GetElements.Response,
    response_model_exclude_none=True,
    response_description="Elements in design project",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_elements(design_project_id: PyObjectUUID, get_elements: GetElementsDep):
    return await get_elements.aexecute(GetElements.Request(project_id=design_project_id))


@router.put(
    f"{ApiPath.ELEMENTS}/{{element_id}}",
    response_model=UpdateElement.Response,
    response_model_exclude_none=True,
    response_description="Element updated in design project",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def update_element(
    design_project_id: PyObjectUUID,
    element_id: PyObjectUUID,
    update_element: UpdateElementDep,
    request: UpdateElement.HttpRequest,
):
    return await update_element.aexecute(
        UpdateElement.Request(
            project_id=design_project_id,
            element_id=element_id,
            element=request.element,
        )
    )


@router.delete(
    f"{ApiPath.ELEMENTS}/{{element_id}}",
    response_model=DeleteElement.Response,
    response_model_exclude_none=True,
    response_description="Element deleted in design project",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def delete_element(design_project_id: PyObjectUUID, element_id: PyObjectUUID, delete_element: DeleteElementDep):
    return await delete_element.aexecute(
        DeleteElement.Request(
            project_id=design_project_id,
            element_id=element_id,
        )
    )
