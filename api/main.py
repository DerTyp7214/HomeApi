from dataclasses import dataclass
import json
import os
import time
from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.routing import Router
from api.auth_bearer import JWTBearer

from api.model import UserLoginSchema, UserSchema

from .routers import main, hue, wled
from .consts import origins, manager
from .auth_handler import check_password, decodeJWT, signJWT
from .db import user_db


app = FastAPI(
    title="Home API",
    description="API for controlling my home",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main.router, prefix="/api")
app.include_router(hue.router, prefix="/api/hue")
app.include_router(wled.router, prefix="/api/wled")

dist = os.path.join(os.path.dirname(__file__), "dist")


def check_user(user: UserLoginSchema) -> bool:
    db_user = user_db.get_user_by_email(user.email)
    if db_user is None:
        return False
    if check_password(user.password, db_user.password):
        return True
    return False


@dataclass
class AuthResponse():
    access_token: str
    token_type: str


@dataclass
class ErrorResponse():
    error: str


@app.post("/api/auth/signup", responses={200: {"model": AuthResponse}, 409: {"model": ErrorResponse}})
def signup(user: UserSchema):
    if user_db.get_user_by_email(user.email) is not None:
        return JSONResponse(status_code=409, content={"error": "Email already exists"})
    if user_db.get_user(user.username) is not None:
        return JSONResponse(status_code=409, content={"error": "Username already exists"})
    user_db.add_user(user)
    return signJWT(user.email)


@app.post("/api/auth/login", responses={200: {"model": AuthResponse}, 401: {"model": ErrorResponse}})
def login(user: UserLoginSchema):
    if check_user(user):
        return JSONResponse(status_code=200, content=signJWT(user.email))
    return JSONResponse(status_code=401, content={"error": "Invalid credentials"})


def getPackageJson():
    with open("package.json", "r") as f:
        return json.load(f)


@dataclass
class StatusResponse():
    status: str
    version: str


@app.get("/api/status", response_model=StatusResponse)
def get_status():
    return JSONResponse(status_code=200, content={"status": "OK", "version": getPackageJson()["version"]})


@app.get("/api/auth/refresh", response_model=AuthResponse)
def refresh(token: str = Depends(JWTBearer())):
    decoded = decodeJWT(token)
    if decoded is None:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    email = decoded["user_id"]
    if email is None:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    return signJWT(email)


@dataclass
class UserResponse():
    email: str


@app.get("/api/auth/me", responses={200: {"model": UserResponse}, 401: {"model": ErrorResponse}})
def me(token: str = Depends(JWTBearer())):
    decoded = decodeJWT(token)
    if decoded is None:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    email = decoded["user_id"]
    if email is None:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    return JSONResponse(status_code=200, content={"email": email})


if os.path.exists(dist):
    static_router = Router()
    static_router.mount(
        "/", StaticFiles(directory=dist, html=True), name="dist")
    app.mount("/static", static_router, name="static")

    @app.get("/")
    def root():
        return RedirectResponse(url="/static")

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
                await websocket.send_text(f"asd")
        except WebSocketDisconnect:
            manager.disconnect(websocket)
