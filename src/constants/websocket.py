from enum import Enum


class WebSocketEvent(str, Enum):
    Ping = "Ping"
    Pong = "Pong"
    Broadcast = "Broadcast"
    Error = "Error"
    Disconnect = "Disconnect"
    # NOTE: sender request events
    CreateElement = "CreateElement"
    DeleteElement = "DeleteElement"
    UpdateElement = "UpdateElement"
    JoinUserCursor = "JoinUserCursor"
    UpdateUserCursor = "UpdateUserCursor"
    # NOTE: sender response events
    ElementCreated = "ElementCreated"
    ElementDeleted = "ElementDeleted"
    ElementUpdated = "ElementUpdated"
    CurrentUsers = "CurrentUsers"
    # NOTE: receiver events
    ReceiveElementCreated = "ReceiveElementCreated"
    ReceiveElementDeleted = "ReceiveElementDeleted"
    ReceiveElementUpdated = "ReceiveElementUpdated"
    ReceiveUserCursorJoined = "ReceiveUserCursorJoined"
    ReceiveUserCursorLeft = "ReceiveUserCursorLeft"
    ReceiveUserCursorUpdated = "ReceiveUserCursorUpdated"
