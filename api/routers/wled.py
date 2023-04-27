from urllib.parse import unquote
from fastapi import APIRouter, Response
import requests
from api.config import config
from api.consts import Wled, WledItem, WledState
from fastapi.responses import JSONResponse

router = APIRouter(
    tags=["wled"],
    responses={404: {"description": "Not found"}},
)


class WledReponseState(Wled):
    ip: str
    name: str


async def allLights() -> list[WledReponseState]:
    lights = []

    for light in config.get_wleds():
        lightResponse = getLight(light.ip)
        if lightResponse is not None:
            lights.append(lightResponse)

    return lights


def getLight(ip: str) -> WledReponseState | None:
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


@router.put("/devices/add")
async def add_device(item: WledItem):
    config.add_wled(item.ip, item.name)
    return Response(status_code=200)


@router.delete("/devices/remove/{ip}")
async def remove_device(ip: str):
    if config.remove_wled(unquote(ip)):
        return Response(status_code=200)
    return JSONResponse(status_code=404, content={"error": "Light not found"})


@router.get("/lights", response_model=list[WledReponseState])
async def lights():
    lights = await allLights()

    return JSONResponse(status_code=200, content=lights)


@router.get("/lights/{ip}", response_model=WledReponseState)
async def light(ip: str):
    light = getLight(ip)

    if light is None:
        return JSONResponse(status_code=404, content={"error": "Light not found"})
    return JSONResponse(status_code=200, content=light)


@router.put("/lights/{ip}/state", response_model=dict)
async def light_state(ip: str, state: WledState):
    response = setLightState(ip, state)

    light = getLight(ip)

    if light is None:
        return JSONResponse(status_code=404, content={"error": "Light not found"})

    if response.status_code == 200:
        return JSONResponse(status_code=200, content=light)

    return response
