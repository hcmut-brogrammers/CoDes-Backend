import json
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.common.models.design_entities.node import NodeModel
from src.components.design_projects.design_entities.nodes.create_node import CreateNode, CreateNodeDep

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.connections.pop(user_id, None)

    async def broadcast(self, sender_id: str, message: str) -> List[str]:
        received_by = []
        for user_id, ws in self.connections.items():
            try:
                await ws.send_text(message)
                if user_id != sender_id:
                    received_by.append(user_id)
            except Exception as e:
                # Log or handle failed send
                pass
        return received_by


manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, create_node: CreateNodeDep):
    print(f"User connected: {user_id}")
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                event = message.get("event")
                payload = message.get("payload")
                header = websocket.headers
                print(header)

                if event == "ping":
                    await websocket.send_text(json.dumps({"event": "pong", "payload": "pong!"}))

                elif event == "echo":
                    await websocket.send_text(json.dumps({"event": "echo", "payload": payload}))

                elif event == "broadcast":
                    node_data = NodeModel(x=3.4, y=2.1)
                    message_to_send = json.dumps(
                        {
                            "event": "broadcast",
                            "from": user_id,
                            "payload": payload,
                            "node": node_data.model_dump(by_alias=True, exclude_none=True),
                        },
                        default=str,
                    )

                    recipients = await manager.broadcast(user_id, message_to_send)

                    # Notify the sender that the message was received by these users
                    await websocket.send_text(
                        json.dumps({"event": "broadcast_ack", "payload": {"delivered_to": recipients}})
                    )
                elif event == "create_node":
                    await websocket.send_text(json.dumps({"event": "echo", "payload": "before"}))
                    result = await create_node.aexecute(CreateNodeDep.Request(**payload))
                    await manager.broadcast(user_id, json.dumps({"event": "echo", "payload": payload}))
                    await websocket.send_text(json.dumps({"event": "echo", "payload": "after"}))
                    pass
                else:
                    await websocket.send_text(json.dumps({"event": "error", "payload": f"Unknown event: {event}"}))
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"event": "error", "payload": "Invalid JSON format"}))
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"User disconnected: {user_id}")
