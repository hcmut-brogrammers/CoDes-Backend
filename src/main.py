import json

from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.routers import websocket

from .exceptions import AppException, ErrorContent, ErrorJSONResponse, ErrorType
from .middlewares.authenticate_middleware import AuthenticateMiddleware
from .routers import authenticate, design_projects, join_workspace_invitations, organizations, tests, users
from .services.jwt_service import JwtService

app = FastAPI(dependencies=[Depends(JwtService)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    return ErrorJSONResponse(
        error_content=ErrorContent(
            error_type=ErrorType.EXCEPTION,
            error_message=exc.error_message,
        ),
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return ErrorJSONResponse(
        error_content=ErrorContent(
            error_type=ErrorType.REQUEST_VALIDATION,
            error_details=exc.errors(),
        ),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


app.add_middleware(AuthenticateMiddleware)

app.include_router(authenticate.router)

app.include_router(users.router)

app.include_router(organizations.router)

app.include_router(join_workspace_invitations.router)

app.include_router(design_projects.router)

app.include_router(websocket.router)

# NOTE: for testing purpose only
app.include_router(tests.router)


# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: list[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_text(message)


# manager = ConnectionManager()


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             try:
#                 message = json.loads(data)
#                 event = message.get("event")
#                 payload = message.get("payload")

#                 if event == "ping":
#                     await websocket.send_text(json.dumps({"event": "pong", "payload": "pong!"}))
#                 elif event == "echo":
#                     await websocket.send_text(json.dumps({"event": "echo", "payload": payload}))
#                 elif event == "broadcast":
#                     await manager.broadcast(json.dumps({"event": "broadcast", "payload": payload}))
#                 else:
#                     await websocket.send_text(json.dumps({"event": "error", "payload": f"Unknown event: {event}"}))
#             except json.JSONDecodeError:
#                 await websocket.send_text(json.dumps({"event": "error", "payload": "Invalid JSON format"}))
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
