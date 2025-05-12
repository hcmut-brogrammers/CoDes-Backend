import typing as t
from enum import Enum

import pydantic as p

from ...common.models import BaseElementModel, ElementModel, PyObjectUUID, UserRole
from ...constants.websocket import WebSocketEvent

ElementTemporaryId = str


class CursorStatus(str, Enum):
    Online = "Online"
    Offline = "Offline"


class CursorPosition(p.BaseModel):
    x: float = p.Field(alias="x")
    y: float = p.Field(alias="y")


class UserCursor(p.BaseModel):
    id: PyObjectUUID = p.Field(alias="id")
    user_id: PyObjectUUID = p.Field(alias="user_id")
    email: str = p.Field(alias="email")
    username: str = p.Field(alias="username")
    position: CursorPosition = p.Field(alias="position", default=CursorPosition(x=0, y=0))
    selected_element_id: PyObjectUUID | None = p.Field(alias="selected_element_id", default=None)
    status: CursorStatus = p.Field(alias="status", default=CursorStatus.Online)


class Sender(p.BaseModel):
    id: PyObjectUUID = p.Field(alias="id")
    username: str = p.Field(alias="username")
    email: str = p.Field(alias="email")
    role: UserRole = p.Field(alias="role")


class ReceiverMessagePayload(p.BaseModel):
    sender: Sender


class IWebSocketMessage[T](p.BaseModel):
    event: WebSocketEvent
    payload: T


class WebSocketMessagePayload:
    # NOTE: sender message request payloads

    class CreateElementMessagePayload(p.BaseModel):
        temporary_element_id: ElementTemporaryId
        element: BaseElementModel

    class DeleteElementMessagePayload(p.BaseModel):
        element_id: PyObjectUUID

    class UpdateElementMessagePayload(p.BaseModel):
        element_id: PyObjectUUID
        element: ElementModel

    class JoinUserCursorMessagePayload(p.BaseModel):
        user_id: PyObjectUUID

    class UpdateUserCursorMessagePayload(p.BaseModel):
        user_cursor: UserCursor

    # NOTE: sender message response payloads

    class ElementCreatedMessagePayload(p.BaseModel):
        temporary_element_id_element_map: dict[ElementTemporaryId, ElementModel]

    class ElementDeletedMessagePayload(p.BaseModel):
        deleted_element_id: PyObjectUUID

    class ElementUpdatedMessagePayload(p.BaseModel):
        updated_element_id: PyObjectUUID
        updated_element: ElementModel

    class CurrentUsersMessagePayload(p.BaseModel):
        users: list[Sender]

    # NOTE: receiver message payloads

    class ReceiveElementCreatedMessagePayload(ReceiverMessagePayload, p.BaseModel):
        element: ElementModel

    class ReceiveElementDeletedMessagePayload(ReceiverMessagePayload, ElementDeletedMessagePayload):
        pass

    class ReceiveElementUpdatedMessagePayload(ReceiverMessagePayload, ElementUpdatedMessagePayload):
        pass

    class ReceiveUserCursorJoinedMessagePayload(ReceiverMessagePayload, p.BaseModel):
        pass

    class ReceiveUserCursorUpdatedMessagePayload(ReceiverMessagePayload, p.BaseModel):
        user_cursor: UserCursor

    class ReceiveUserCursorLeftMessagePayload(ReceiverMessagePayload, p.BaseModel):
        pass

    # NOTE: other message payloads

    class PingMessagePayload(p.BaseModel):
        message: str

    class PongMessagePayload(p.BaseModel):
        message: str

    class BroadcastMessagePayload(p.BaseModel):
        sender: Sender
        message: str

    class ErrorMessagePayload(p.BaseModel):
        message: str

    class DisconnectMessagePayload(p.BaseModel):
        message: str


class WebSocketMessage:
    # NOTE: sender request messages

    class CreateElementMessage(IWebSocketMessage[WebSocketMessagePayload.CreateElementMessagePayload]):
        event: t.Literal[WebSocketEvent.CreateElement] = WebSocketEvent.CreateElement

    class DeleteElementMessage(IWebSocketMessage[WebSocketMessagePayload.DeleteElementMessagePayload]):
        event: t.Literal[WebSocketEvent.DeleteElement] = WebSocketEvent.DeleteElement

    class UpdateElementMessage(IWebSocketMessage[WebSocketMessagePayload.UpdateElementMessagePayload]):
        event: t.Literal[WebSocketEvent.UpdateElement] = WebSocketEvent.UpdateElement

    class JoinUserCursorMessage(IWebSocketMessage[WebSocketMessagePayload.JoinUserCursorMessagePayload]):
        event: t.Literal[WebSocketEvent.JoinUserCursor] = WebSocketEvent.JoinUserCursor

    class UpdateUserCursorMessage(IWebSocketMessage[WebSocketMessagePayload.UpdateUserCursorMessagePayload]):
        event: t.Literal[WebSocketEvent.UpdateUserCursor] = WebSocketEvent.UpdateUserCursor

    # NOTE: sender response messages

    class ElementCreatedMessage(IWebSocketMessage[WebSocketMessagePayload.ElementCreatedMessagePayload]):
        event: t.Literal[WebSocketEvent.ElementCreated] = WebSocketEvent.ElementCreated

    class ElementDeletedMessage(IWebSocketMessage[WebSocketMessagePayload.ElementDeletedMessagePayload]):
        event: t.Literal[WebSocketEvent.ElementDeleted] = WebSocketEvent.ElementDeleted

    class ElementUpdatedMessage(IWebSocketMessage[WebSocketMessagePayload.ElementUpdatedMessagePayload]):
        event: t.Literal[WebSocketEvent.ElementUpdated] = WebSocketEvent.ElementUpdated

    class CurrentUsersMessage(IWebSocketMessage[WebSocketMessagePayload.CurrentUsersMessagePayload]):
        event: t.Literal[WebSocketEvent.CurrentUsers] = WebSocketEvent.CurrentUsers

    # NOTE: receiver messages

    class ReceiveElementCreatedMessage(IWebSocketMessage[WebSocketMessagePayload.ReceiveElementCreatedMessagePayload]):
        event: t.Literal[WebSocketEvent.ReceiveElementCreated] = WebSocketEvent.ReceiveElementCreated

    class ReceiveElementDeletedMessage(IWebSocketMessage[WebSocketMessagePayload.ReceiveElementDeletedMessagePayload]):
        event: t.Literal[WebSocketEvent.ReceiveElementDeleted] = WebSocketEvent.ReceiveElementDeleted

    class ReceiveElementUpdatedMessage(IWebSocketMessage[WebSocketMessagePayload.ReceiveElementUpdatedMessagePayload]):
        event: t.Literal[WebSocketEvent.ReceiveElementUpdated] = WebSocketEvent.ReceiveElementUpdated

    class ReceiveUserCursorJoinedMessage(
        IWebSocketMessage[WebSocketMessagePayload.ReceiveUserCursorJoinedMessagePayload]
    ):
        event: t.Literal[WebSocketEvent.ReceiveUserCursorJoined] = WebSocketEvent.ReceiveUserCursorJoined

    class ReceiveUserCursorLeftMessage(IWebSocketMessage[WebSocketMessagePayload.ReceiveUserCursorLeftMessagePayload]):
        event: t.Literal[WebSocketEvent.ReceiveUserCursorLeft] = WebSocketEvent.ReceiveUserCursorLeft

    class ReceiveUserCursorUpdatedMessage(
        IWebSocketMessage[WebSocketMessagePayload.ReceiveUserCursorUpdatedMessagePayload]
    ):
        event: t.Literal[WebSocketEvent.ReceiveUserCursorUpdated] = WebSocketEvent.ReceiveUserCursorUpdated

    # NOTE: other messagemessages

    class PingMessage(IWebSocketMessage[WebSocketMessagePayload.PingMessagePayload]):
        event: t.Literal[WebSocketEvent.Ping] = WebSocketEvent.Ping

    class PongMessage(IWebSocketMessage[WebSocketMessagePayload.PongMessagePayload]):
        event: t.Literal[WebSocketEvent.Pong] = WebSocketEvent.Pong

    class BroadcastMessage(IWebSocketMessage[WebSocketMessagePayload.BroadcastMessagePayload]):
        event: t.Literal[WebSocketEvent.Broadcast] = WebSocketEvent.Broadcast

    class ErrorMessage(IWebSocketMessage[WebSocketMessagePayload.ErrorMessagePayload]):
        event: t.Literal[WebSocketEvent.Error] = WebSocketEvent.Error

    class DisconnectMessage(IWebSocketMessage[WebSocketMessagePayload.DisconnectMessagePayload]):
        event: t.Literal[WebSocketEvent.Disconnect] = WebSocketEvent.Disconnect
