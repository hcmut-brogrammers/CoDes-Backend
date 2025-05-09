import typing as t

from fastapi import Depends, WebSocket, WebSocketException, status

from ...services.jwt_service import JwtServiceDep
from . import UserContext


async def get_websocket_user_context(websocket: WebSocket, jwt_service: JwtServiceDep):
    token = websocket.query_params.get("access_token")
    if not token:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Missing access token")

    try:
        payload = jwt_service.decode_jwt_token(token)
        return UserContext(**payload.model_dump())
    except ValueError:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid access token")


WebsocketUserContextDep = t.Annotated[UserContext, Depends(get_websocket_user_context)]
