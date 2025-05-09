import typing as t

import pydantic as p

from ...common.models import BaseElementModel, ElementModel, PyObjectUUID, UserRole
from ...constants.websocket import WebSocketEvent

ElementTemporaryId = str


class UserCursor(p.BaseModel):
    user_id: PyObjectUUID
    username: str
    x: float
    y: float


class Sender(p.BaseModel):
    id: PyObjectUUID
    username: str
    email: str
    role: UserRole


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

    class JoinProjectMessagePayload(p.BaseModel):
        user_id: PyObjectUUID

    class MoveCursorMessagePayload(p.BaseModel):
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

    class ReceiveUserJoinedProjectMessagePayload(ReceiverMessagePayload, p.BaseModel):
        pass

    class ReceiveUserCursorMovedMessagePayload(ReceiverMessagePayload, p.BaseModel):
        sender_cursor: UserCursor

    class ReceiveUserLeavedProjectMessagePayload(ReceiverMessagePayload, p.BaseModel):
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

    class JoinProjectMessage(IWebSocketMessage[WebSocketMessagePayload.JoinProjectMessagePayload]):
        event: t.Literal[WebSocketEvent.JoinProject] = WebSocketEvent.JoinProject

    class MoveCursorMessage(IWebSocketMessage[WebSocketMessagePayload.MoveCursorMessagePayload]):
        event: t.Literal[WebSocketEvent.MoveCursor] = WebSocketEvent.MoveCursor

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

    class ReceiveUserJoinedProjectMessage(
        IWebSocketMessage[WebSocketMessagePayload.ReceiveUserJoinedProjectMessagePayload]
    ):
        event: t.Literal[WebSocketEvent.ReceiveUserJoinedProject] = WebSocketEvent.ReceiveUserJoinedProject

    class ReceiveUserLeavedProjectMessage(
        IWebSocketMessage[WebSocketMessagePayload.ReceiveUserLeavedProjectMessagePayload]
    ):
        event: t.Literal[WebSocketEvent.ReceiveUserLeftProject] = WebSocketEvent.ReceiveUserLeftProject

    class ReceiveUserCursorMovedMessage(
        IWebSocketMessage[WebSocketMessagePayload.ReceiveUserCursorMovedMessagePayload]
    ):
        event: t.Literal[WebSocketEvent.ReceiveUserCursorMoved] = WebSocketEvent.ReceiveUserCursorMoved

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
