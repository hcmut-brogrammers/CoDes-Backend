from uuid import UUID

from fastapi import APIRouter, status

from ...components.products import CreateProductDep, GetProductByIdDep
from ...constants.router import ApiPath

router = APIRouter(
    prefix=ApiPath.PRODUCTS,
    tags=["products"],
)


@router.get(
    "/{product_id}",
    response_model=GetProductByIdDep.Response,
    response_description="Product retrieved",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_product_id(get_product_id: GetProductByIdDep, product_id: UUID):
    return await get_product_id.aexecute(GetProductByIdDep.Request(product_id=product_id))


@router.post(
    "",
    response_model=CreateProductDep.Response,
    response_description="Product created",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(create_product: CreateProductDep, request: CreateProductDep.Request):
    return await create_product.aexecute(request)


# @router.put(
#     "/{organization_id}",
#     response_model=UpdateOrganizationDep.Response,
#     response_description="Organization updated",
#     response_model_by_alias=False,
#     status_code=status.HTTP_200_OK,
# )
# async def update_organization(
#     update_organization: UpdateOrganizationDep, organization_id: UUID, request: UpdateOrganizationDep.HttpRequest
# ):
#     return await update_organization.aexecute(
#         UpdateOrganizationDep.Request(organization_id=organization_id, **request.model_dump())
#     )


# @router.delete(
#     "/{organization_id}",
#     response_model=DeleteOrganizationByIdDep.Response,
#     response_description="Organization deleted",
#     response_model_by_alias=False,
#     status_code=status.HTTP_200_OK,
# )
# async def delete_organization_by_id(deleted_organization: DeleteOrganizationByIdDep, organization_id: UUID):
#     return await deleted_organization.aexecute(DeleteOrganizationByIdDep.Request(organization_id=organization_id))
