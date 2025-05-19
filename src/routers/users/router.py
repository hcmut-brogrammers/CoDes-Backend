from fastapi import APIRouter, status

from ...common.models import PyObjectUUID
from ...components.users import GetMe, GetMeDep, GetUserByEmailFragmentDep, UpdateUserDep
from ...constants.router import ApiPath

router = APIRouter(
    prefix=ApiPath.USERS,
    tags=["users"],
)


@router.get(
    "/me",
    response_model=GetMe.Response,
    response_description="Get current user info",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_users(get_me: GetMeDep):
    return await get_me.aexecute()


@router.get(
    "",
    response_model=GetUserByEmailFragmentDep.Response,
    response_description="List of users",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_users_by_email_fragment(get_users: GetUserByEmailFragmentDep, email: str):
    return await get_users.aexecute(GetUserByEmailFragmentDep.Request(email_fragment=email))


@router.put(
    "/{user_id}",
    response_model=UpdateUserDep.Response,
    response_description="User updated",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def update_user(update_user: UpdateUserDep, user_id: PyObjectUUID, request: UpdateUserDep.HttpRequest):
    return await update_user.aexecute(UpdateUserDep.Request(user_id=user_id, **request.model_dump()))
