import json
from typing import Optional
from fastapi import WebSocket
from pydantic import BaseModel


class LightColor(BaseModel):
    hue: Optional[float] = None
    saturation: Optional[float] = None


class LightState(BaseModel):
    on: Optional[bool] = None
    brightness: Optional[float] = None
    color: Optional[LightColor] = None


class HueLightState(BaseModel):
    on: Optional[bool] = None
    bri: Optional[float] = None
    hue: Optional[float] = None
    sat: Optional[float] = None


class PlugState(LightState):
    on: bool


class HuePlugState(HueLightState):
    on: bool


class WebSocketMessage(BaseModel):
    type: str
    data: dict


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


async def broadcast(message: WebSocketMessage):
    await manager.broadcast(json.dumps(message.dict()))


origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:433",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:5173",
]
