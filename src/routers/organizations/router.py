from uuid import UUID

from fastapi import APIRouter, status

from ...components.organizations import CreateOrganizationDep, GetOrganizationByOwnerIdDep
from ...constants.router import ApiPath

router = APIRouter(
    prefix=ApiPath.ORGANIZATIONS,
    tags=["organizations"],
)


@router.get(
    "",
    response_model=GetOrganizationByOwnerIdDep.Response,
    response_description="List of organizations",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_organizations_by_owner_id(get_organizations_by_owner_id: GetOrganizationByOwnerIdDep):
    return await get_organizations_by_owner_id.aexecute()


@router.post(
    "",
    response_model=CreateOrganizationDep.Response,
    response_description="Organization created",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(create_organization: CreateOrganizationDep, request: CreateOrganizationDep.Request):
    return await create_organization.aexecute(request)
