from urllib.parse import unquote
from fastapi import APIRouter, Depends, Response
import requests
from api.auth_bearer import JWTBearer
from api.db import user_db
from api.consts import ErrorResponse, Wled, WledItem, WledState
from fastapi.responses import JSONResponse

from api.model import UserSchema

router = APIRouter(
    tags=["wled"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(JWTBearer())]
)


class WledReponseState(Wled):
    ip: str
    name: str


async def allLights(token: str) -> list[WledReponseState]:
    lights = []
    config = user_db.config_db_by_token(token)
    if config is None:
        return lights
    for light in config.get_wleds():
        lightResponse = getLight(token, light.ip)
        if lightResponse is not None:
            lights.append(lightResponse)

    return lights


def getLight(token: str, ip: str) -> WledReponseState | None:
    config = user_db.config_db_by_token(token)
    if config is None:
        return None
    wled = config.get_wled(ip)
    if wled is None:
        return None

    try:
        response = requests.get(f"http://{ip}/json")

        data: dict = response.json()
        data.update({
            "ip": ip,
            "name": wled.name,
        })
        return WledReponseState.from_dict(data)
    except:
        return None


def setLightState(ip: str, state: WledState):
    return requests.post(f"http://{ip}/json/state", json=state.to_dict())


@router.put("/devices/add", responses={401: {"model": ErrorResponse}, 200: {"model": str}})
async def add_device(item: WledItem, token: str = Depends(JWTBearer())):
    config = user_db.config_db_by_token(token)
    if config is None:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    config.add_wled(item.ip, item.name)
    return Response(status_code=200)


@router.delete("/devices/remove/{ip}", responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 200: {"model": str}})
async def remove_device(ip: str, token: str = Depends(JWTBearer())):
    config = user_db.config_db_by_token(token)
    if config is None:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    if config.remove_wled(unquote(ip)):
        return Response(status_code=200)
    return JSONResponse(status_code=404, content={"error": "Light not found"})


@router.get("/lights", response_model=list[WledReponseState])
async def lights(token: str = Depends(JWTBearer())):
    lights = await allLights(token)

    return JSONResponse(status_code=200, content=lights)


@router.get("/lights/{ip}", responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 200: {"model": WledReponseState}})
async def light(ip: str, token: str = Depends(JWTBearer())):
    light = getLight(token, ip)

    if light is None:
        return JSONResponse(status_code=404, content={"error": "Light not found"})
    return JSONResponse(status_code=200, content=light)


@router.put("/lights/{ip}/state", responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 200: {"model": WledReponseState}})
async def light_state(ip: str, state: WledState, token: str = Depends(JWTBearer())):
    response = setLightState(ip, state)

    light = getLight(token, ip)

    if light is None:
        return JSONResponse(status_code=404, content={"error": "Light not found"})

    if response.status_code == 200:
        return JSONResponse(status_code=200, content=light)

    return response
