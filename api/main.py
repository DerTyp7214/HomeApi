import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.routing import Router

from .routers import main, hue

from .types import origins, manager

app = FastAPI(
    title="Home API",
    description="API for controlling my home",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_router = Router()

static_router.mount(
    "/", StaticFiles(directory="api\\dist", html=True), name="dist")

app.mount("/static", static_router, name="static")
app.include_router(main.router, prefix="/api")
app.include_router(hue.router, prefix="/api/hue")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
            await websocket.send_text(f"asd")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
