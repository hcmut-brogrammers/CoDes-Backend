import pydantic as p
from fastapi.websockets import WebSocket

from ...common.models import PyObjectUUID
from ...common.websocket.message import Sender
from ...dependencies import create_logger

DesignProjectId = PyObjectUUID
ClientId = PyObjectUUID


class WebSocketClient(p.BaseModel):
    client: Sender
    websocket: WebSocket

    model_config = p.ConfigDict(
        arbitrary_types_allowed=True,
    )


WebSocketConnection = dict[ClientId, WebSocketClient]

WebSocketConnections = dict[DesignProjectId, WebSocketConnection]


class ClientConnectionManager:
    def __init__(self) -> None:
        self._connections: WebSocketConnections = {}
        self._logger = create_logger()

    async def connect(self, design_project_id: PyObjectUUID, client: Sender, websocket: WebSocket) -> None:
        client_id = client.id
        connection = self._connections.pop(design_project_id, None) or {}
        if client_id in connection.keys():
            return

        await websocket.accept()
        connection[client_id] = WebSocketClient(client=client, websocket=websocket)
        self._connections[design_project_id] = connection
        self._logger.info(
            f"WebSocket connection established for client {client_id} in design project {design_project_id}."
        )
        self._logger.info(f"Current connections: {self._connections}")

    async def disconnect(self, design_project_id: PyObjectUUID, client_id: PyObjectUUID) -> None:
        if design_project_id not in self._connections.keys():
            return

        if client_id not in self._connections[design_project_id].keys():
            return

        self._connections[design_project_id].pop(client_id, None)
        self._logger.info(f"WebSocket connection closed for client {client_id} from design project {design_project_id}")

        if not len(self._connections[design_project_id].keys()):
            self._connections.pop(design_project_id, None)
            self._logger.info(f"All connections closed for design project {design_project_id}")

    async def broadcast(self, design_project_id: PyObjectUUID, sender_id: PyObjectUUID, message: dict) -> None:
        if design_project_id not in self._connections.keys():
            return

        if sender_id not in self._connections[design_project_id].keys():
            return

        for client_id, websocket_client in self._connections[design_project_id].items():
            websocket = websocket_client.websocket
            try:
                if client_id != sender_id:
                    await websocket.send_json(message)
            except Exception as e:
                self._logger.info(
                    f"Failed to send message to client {client_id} in design project {design_project_id}: {e}"
                )

    def get_clients(self, design_project_id: PyObjectUUID) -> list[Sender]:
        if design_project_id not in self._connections.keys():
            return []

        return [websocket_client.client for websocket_client in self._connections[design_project_id].values()]

    def get_broadcast_clients(self, design_project_id: PyObjectUUID, client_id: PyObjectUUID) -> list[Sender]:
        clients = self.get_clients(design_project_id)
        return [client for client in clients if client.id != client_id]
