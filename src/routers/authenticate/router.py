from fastapi import APIRouter

from ...components.authenticate import (
    AuthenticateUser,
    AuthenticateUserDep,
    RefreshAccessToken,
    RefreshAccessTokenDep,
    SignUp,
    SignUpDep,
)
from ...constants.router import ApiPath

router = APIRouter(
    prefix=ApiPath.AUTHENTICATE,
    tags=["authenticate"],
)


@router.post(
    ApiPath.SIGN_UP,
    response_model=SignUp.Response,
    response_description="User email signed up successfully",
    response_model_by_alias=False,
    status_code=201,
)
async def create_token(create_token: SignUpDep, request: SignUp.Request):
    return await create_token.aexecute(request)


@router.post(
    ApiPath.AUTHENTICATE_USER,
    response_model=AuthenticateUser.Response,
    response_description="User email authenticated successfully",
    response_model_by_alias=False,
    status_code=200,
)
async def authenticate_user(authenticate_user: AuthenticateUserDep, request: AuthenticateUser.Request):
    return await authenticate_user.aexecute(request)


@router.post(
    ApiPath.REFRESH_ACCESS_TOKEN,
    response_model=RefreshAccessToken.Response,
    response_description="Access token refreshed successfully",
    response_model_by_alias=False,
    status_code=200,
)
async def refresh_access_token(refresh_access_token: RefreshAccessTokenDep, request: RefreshAccessToken.Request):
    return await refresh_access_token.aexecute(request)
