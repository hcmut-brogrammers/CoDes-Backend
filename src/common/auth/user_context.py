import typing as t

from fastapi import Depends, Request

from .token_data import TokenData


class UserContext(TokenData):
    pass


def get_user_context(request: Request) -> UserContext:
    if not hasattr(request.state, "token_data"):
        raise ValueError("Token data not found in request context")

    if not isinstance(request.state.token_data, TokenData):
        raise ValueError("Token data is not of type TokenData")

    return UserContext(**t.cast(TokenData, request.state.token_data).model_dump())


UserContextDep = t.Annotated[UserContext, Depends(get_user_context)]
