import json
import typing as t

import pydantic as p
from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket, WebSocketDisconnect

from ...common.auth.websocket_user_context import WebsocketUserContextDep
from ...common.models import BaseCircleModel, BaseElementModel, BaseRectangleModel, PyObjectUUID
from ...common.websocket.connection_manager import ClientConnectionManager, Sender
from ...common.websocket.message import IWebSocketMessage, Sender, WebSocketMessage, WebSocketMessagePayload
from ...components.design_projects.elements import (
    BaseCreateElement,
    BaseCreateElementDep,
    BaseDeleteElement,
    BaseDeleteElementDep,
    BaseUpdateElement,
    BaseUpdateElementDep,
)
from ...constants.websocket import WebSocketEvent
from ...dependencies import LoggerDep
from ...utils.design_element import BaseElementTypeChecker, create_element
from ...utils.logger import execute_service_method

client_connection_manager = ClientConnectionManager()

TBaseModel = t.TypeVar("TBaseModel", bound=p.BaseModel)


class WebsocketHandler:
    def __init__(
        self,
        websocket: WebSocket,
        websocket_user_context: WebsocketUserContextDep,
        base_create_element: BaseCreateElementDep,
        logger: LoggerDep,
        base_delete_element: BaseDeleteElementDep,
        base_update_element: BaseUpdateElementDep,
    ) -> None:
        self._websocket = websocket
        self._user_context = websocket_user_context
        self._base_create_element = base_create_element
        self._logger = logger
        self._base_delete_element = base_delete_element
        self._base_update_element = base_update_element

    async def send_message(self, message: IWebSocketMessage) -> None:
        await self._websocket.send_json(message.model_dump(mode="json", by_alias=False, exclude_none=True))

    async def broadcast_message(
        self, design_project_id: PyObjectUUID, client_id: PyObjectUUID, message: IWebSocketMessage
    ) -> None:
        await client_connection_manager.broadcast(
            design_project_id,
            client_id,
            message.model_dump(mode="json", by_alias=False, exclude_none=True),
        )

    def _create_sender(self) -> Sender:
        return Sender(
            id=self._user_context.user_id,
            username=self._user_context.username,
            email=self._user_context.email,
            role=self._user_context.role,
        )

    async def _validate_payload(self, payload: dict, cls: type[TBaseModel]) -> TBaseModel | None:
        try:
            return cls.model_validate(payload)
        except p.ValidationError as e:
            print(f"Failed to validate payload: {e}")
            error_message = WebSocketMessage.ErrorMessage(
                payload=WebSocketMessagePayload.ErrorMessagePayload(message=f"Failed to validate payload: {e}")
            )
            await self.send_message(error_message)
            return None

    async def _handle_ping_message(self) -> None:
        self._logger.info(execute_service_method(self))
        pong_message = WebSocketMessage.PongMessage(
            payload=WebSocketMessagePayload.PongMessagePayload(message="I received your ping!")
        )
        await self.send_message(pong_message)

    async def _handle_broadcast_message(self, design_project_id: PyObjectUUID, client_id: PyObjectUUID) -> None:
        self._logger.info(execute_service_method(self))
        broadcast_message = WebSocketMessage.BroadcastMessage(
            payload=WebSocketMessagePayload.BroadcastMessagePayload(
                sender=self._create_sender(),
                message="This message is broadcasted to all clients from the server",
            )
        )
        await self.broadcast_message(design_project_id, client_id, broadcast_message)

    async def _handle_create_element_message(
        self, design_project_id: PyObjectUUID, client_id: PyObjectUUID, payload: dict
    ) -> None:
        self._logger.info(execute_service_method(self))
        create_element_message_payload = await self._validate_payload(
            payload, WebSocketMessagePayload.CreateElementMessagePayload
        )
        if not create_element_message_payload:
            return

        element = create_element_message_payload.element

        base_create_element_request = BaseCreateElement.Request(
            design_project_id=design_project_id,
            organization_id=self._user_context.organization_id,
            element=element,
        )
        base_create_element_response = await self._base_create_element.aexecute(base_create_element_request)
        created_element = base_create_element_response.created_element
        temporary_element_id = create_element_message_payload.temporary_element_id
        element_created_message = WebSocketMessage.ElementCreatedMessage(
            payload=WebSocketMessagePayload.ElementCreatedMessagePayload(
                temporary_element_id_element_map={temporary_element_id: created_element},
            )
        )
        await self.send_message(element_created_message)

        retrieve_element_created_message = WebSocketMessage.ReceiveElementCreatedMessage(
            payload=WebSocketMessagePayload.ReceiveElementCreatedMessagePayload(
                sender=self._create_sender(),
                element=created_element,
            )
        )
        await self.broadcast_message(
            design_project_id,
            client_id,
            retrieve_element_created_message,
        )

    async def _handle_delete_element_message(
        self, design_project_id: PyObjectUUID, client_id: PyObjectUUID, payload: dict
    ) -> None:
        self._logger.info(execute_service_method(self))
        delete_element_message_payload = await self._validate_payload(
            payload, WebSocketMessagePayload.DeleteElementMessagePayload
        )
        if not delete_element_message_payload:
            return

        element_id = delete_element_message_payload.element_id
        base_delete_element_request = BaseDeleteElement.Request(
            organization_id=self._user_context.organization_id,
            project_id=design_project_id,
            element_id=element_id,
        )
        base_delete_element_response = await self._base_delete_element.aexecute(base_delete_element_request)
        if not base_delete_element_response.success:
            error_message = WebSocketMessage.ErrorMessage(
                payload=WebSocketMessagePayload.ErrorMessagePayload(message="Failed to delete element")
            )
            await self.send_message(error_message)
            return

        element_deleted_message = WebSocketMessage.ElementDeletedMessage(
            payload=WebSocketMessagePayload.ElementDeletedMessagePayload(
                deleted_element_id=element_id,
            )
        )
        await self.send_message(element_deleted_message)

        receive_element_deleted_message = WebSocketMessage.ReceiveElementDeletedMessage(
            payload=WebSocketMessagePayload.ReceiveElementDeletedMessagePayload(
                sender=self._create_sender(),
                deleted_element_id=element_id,
            )
        )
        await self.broadcast_message(
            design_project_id,
            client_id,
            receive_element_deleted_message,
        )

    async def _handle_update_element_message(
        self, design_project_id: PyObjectUUID, client_id: PyObjectUUID, payload: dict
    ) -> None:
        self._logger.info(execute_service_method(self))
        update_element_message_payload = await self._validate_payload(
            payload, WebSocketMessagePayload.UpdateElementMessagePayload
        )
        if not update_element_message_payload:
            return

        element = update_element_message_payload.element
        element_id = update_element_message_payload.element_id
        base_delete_element_request = BaseUpdateElement.Request(
            organization_id=self._user_context.organization_id,
            project_id=design_project_id,
            element_id=element_id,
            element=element,
        )
        base_update_element_response = await self._base_update_element.aexecute(base_delete_element_request)
        if not base_update_element_response:
            error_message = WebSocketMessage.ErrorMessage(
                payload=WebSocketMessagePayload.ErrorMessagePayload(message="Failed to update element")
            )
            await self.send_message(error_message)
            return

        updated_element = base_update_element_response.updated_element
        element_updated_message = WebSocketMessage.ElementUpdatedMessage(
            payload=WebSocketMessagePayload.ElementUpdatedMessagePayload(
                updated_element_id=updated_element.id, updated_element=updated_element
            )
        )
        await self.send_message(element_updated_message)

        receive_element_updated_message = WebSocketMessage.ReceiveElementUpdatedMessage(
            payload=WebSocketMessagePayload.ReceiveElementUpdatedMessagePayload(
                sender=self._create_sender(),
                updated_element_id=updated_element.id,
                updated_element=updated_element,
            )
        )
        await self.broadcast_message(
            design_project_id,
            client_id,
            receive_element_updated_message,
        )

    async def _handle_join_user_cursor_message(
        self, design_project_id: PyObjectUUID, client_id: PyObjectUUID, payload: dict
    ) -> None:
        self._logger.info(execute_service_method(self))
        join_project_message = await self._validate_payload(
            payload, WebSocketMessagePayload.JoinUserCursorMessagePayload
        )
        if not join_project_message:
            return

        broadcast_clients = client_connection_manager.get_broadcast_clients(design_project_id, client_id)
        current_users_message = WebSocketMessage.CurrentUsersMessage(
            payload=WebSocketMessagePayload.CurrentUsersMessagePayload(users=broadcast_clients)
        )
        await self.send_message(current_users_message)

        receive_user_joined_project_message = WebSocketMessage.ReceiveUserCursorJoinedMessage(
            payload=WebSocketMessagePayload.ReceiveUserCursorJoinedMessagePayload(
                sender=self._create_sender(),
            )
        )
        await self.broadcast_message(
            design_project_id,
            client_id,
            receive_user_joined_project_message,
        )

    async def _handle_update_user_cursor_message(
        self, design_project_id: PyObjectUUID, client_id: PyObjectUUID, payload: dict
    ) -> None:
        move_cursor_message_payload = await self._validate_payload(
            payload, WebSocketMessagePayload.UpdateUserCursorMessagePayload
        )
        if not move_cursor_message_payload:
            return

        receive_user_cursor_moved_message = WebSocketMessage.ReceiveUserCursorUpdatedMessage(
            payload=WebSocketMessagePayload.ReceiveUserCursorUpdatedMessagePayload(
                sender=self._create_sender(),
                user_cursor=move_cursor_message_payload.user_cursor,
            )
        )
        await self.broadcast_message(
            design_project_id,
            client_id,
            receive_user_cursor_moved_message,
        )

    async def handle_disconnected_client(self, design_project_id: PyObjectUUID) -> None:
        self._logger.info(execute_service_method(self))
        client_id = self._user_context.user_id
        receive_user_leaved_project_message = WebSocketMessage.ReceiveUserCursorLeftMessage(
            payload=WebSocketMessagePayload.ReceiveUserCursorLeftMessagePayload(
                sender=self._create_sender(),
            )
        )
        await self.broadcast_message(
            design_project_id,
            client_id,
            receive_user_leaved_project_message,
        )

        await client_connection_manager.disconnect(design_project_id, client_id)

    async def handle_event(self, design_project_id: PyObjectUUID, message: dict) -> None:
        client_id = self._user_context.user_id
        # TODO: validate message
        event = t.cast(WebSocketEvent, message.get("event"))
        payload = t.cast(dict, message.get("payload"))
        if event == WebSocketEvent.Ping:
            await self._handle_ping_message()
        elif event == WebSocketEvent.Broadcast:
            await self._handle_broadcast_message(
                design_project_id,
                client_id,
            )
        elif event == WebSocketEvent.CreateElement:
            await self._handle_create_element_message(design_project_id, client_id, payload)
        elif event == WebSocketEvent.DeleteElement:
            await self._handle_delete_element_message(design_project_id, client_id, payload)
        elif event == WebSocketEvent.UpdateElement:
            await self._handle_update_element_message(design_project_id, client_id, payload)
        elif event == WebSocketEvent.JoinUserCursor:
            await self._handle_join_user_cursor_message(design_project_id, client_id, payload)
        elif event == WebSocketEvent.UpdateUserCursor:
            return await self._handle_update_user_cursor_message(design_project_id, client_id, payload)
        else:
            error_message = WebSocketMessage.ErrorMessage(
                payload=WebSocketMessagePayload.ErrorMessagePayload(message="Unknown event")
            )
            await self._websocket.send_json(error_message.model_dump(mode="json", by_alias=False, exclude_none=True))


WebsocketHandlerDep = t.Annotated[WebsocketHandler, Depends()]


router = APIRouter()


@router.websocket("/ws/design-projects/{design_project_id}")
async def websocket_client_endpoitn(
    websocket: WebSocket,
    websocket_handler: WebsocketHandlerDep,
    websocket_user_context: WebsocketUserContextDep,
    design_project_id: PyObjectUUID,
) -> None:
    client_id = websocket_user_context.user_id
    await client_connection_manager.connect(design_project_id, create_client(websocket_user_context), websocket)
    try:
        while True:
            try:
                message = await websocket.receive_json()
                await websocket_handler.handle_event(design_project_id, message)
            except json.JSONDecodeError:
                error_message = WebSocketMessage.ErrorMessage(
                    payload=WebSocketMessagePayload.ErrorMessagePayload(message="Invalid JSON payload")
                )
                await websocket_handler.send_message(error_message)
    except WebSocketDisconnect as e:
        await websocket_handler.handle_disconnected_client(design_project_id)
        disconnect_message = WebSocketMessage.DisconnectMessage(
            payload=WebSocketMessagePayload.DisconnectMessagePayload(
                message=f"Client {client_id} disconnected",
            )
        )
        await websocket_handler.broadcast_message(design_project_id, client_id, disconnect_message)


def create_client(websocket_user_context: WebsocketUserContextDep) -> Sender:
    return Sender(
        id=websocket_user_context.user_id,
        username=websocket_user_context.username,
        email=websocket_user_context.email,
        role=websocket_user_context.role,
    )
