from uuid import UUID

from fastapi import APIRouter, status

from ...components.users import CreateUserDep, DeleteUserByIdDep, GetUserByIdDep, UpdateUserDep

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/{user_id}",
    response_model=GetUserByIdDep.Response,
    response_description="List of users",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_users(get_users: GetUserByIdDep, user_id: UUID):
    return await get_users.aexecute(GetUserByIdDep.Request(user_id=user_id))


@router.post(
    "",
    response_model=CreateUserDep.Response,
    response_description="User created",
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(create_user: CreateUserDep, request: CreateUserDep.Request):
    return await create_user.aexecute(request)


@router.put(
    "/{user_id}",
    response_model=UpdateUserDep.Response,
    response_description="User updated",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def update_user(update_user: UpdateUserDep, user_id: UUID, request: UpdateUserDep.HttpRequest):
    return await update_user.aexecute(UpdateUserDep.Request(user_id=user_id, **request.model_dump()))


@router.delete(
    "/{user_id}",
    response_model=DeleteUserByIdDep.Response,
    response_description="User deleted",
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def delete_user(delete_user: DeleteUserByIdDep, user_id: UUID):
    return await delete_user.aexecute(DeleteUserByIdDep.Request(user_id=user_id))
