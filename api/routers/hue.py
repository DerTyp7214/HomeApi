import json
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests

from api.consts import HueConfig, HueLightResponse, HueLightState, HuePlugResponse, HuePlugState, Light, LightState, Plug, WebSocketMessage, broadcast
from api.config import config

router = APIRouter(
    tags=["hue"],
    responses={404: {"description": "Not found"}},
)


def mapLight(light, id: int) -> Light | None:
    if "colormode" not in light["state"]:
        return None

    light = {
        "id": f"hue-{id}",
        "name": light["name"],
        "on": light["state"]["on"],
        "brightness": float(light["state"]["bri"]) / 255,
        "color": {
            "hue": float(light["state"]["hue"]) / 65535 * 360,
            "saturation": float(light["state"]["sat"]) / 255 * 100,
        },
        "reachable": light["state"]["reachable"],
        "type": light["type"],
        "model": light["modelid"],
        "manufacturer": light["manufacturername"],
        "uniqueid": light["uniqueid"],
        "swversion": light["swversion"],
        "productid": light["productid"]
    }

    return Light.from_dict(light)


def mapPlug(plug, id: int) -> Plug | None:
    if plug["config"]["archetype"] != "plug":
        return None

    new_plug = {
        "id": f"hue-{id}",
        "name": plug["name"],
        "on": plug["state"]["on"],
        "reachable": plug["state"]["reachable"],
        "type": plug["type"],
        "model": plug["modelid"],
        "manufacturer": plug["manufacturername"],
        "uniqueid": plug["uniqueid"],
        "swversion": plug["swversion"],
        "productid": plug["productid"]
    }

    return Plug.from_dict(new_plug)


def getLights():
    user, host = config.get_hue_user(), config.get_hue_host()
    if host == "" or user == "":
        return []
    lights = requests.get(
        f"http://{host}/api/{user}/lights")
    return lights.json()


def getNormalizedLights():
    lights = getLights()
    normalizedLights = []
    for light in lights:
        normalized = mapLight(lights[light], light)
        if normalized is not None:
            normalizedLights.append(normalized)
    return normalizedLights


def getLight(id: int):
    user, host = config.get_hue_user(), config.get_hue_host()
    if host == "" or user == "":
        return None
    light = requests.get(
        f"http://{host}/api/{user}/lights/{id}")
    return light.json()


def getNormalizedLight(id: int):
    light = getLight(id)
    normalizedLight = mapLight(light, id)
    return normalizedLight


def getPlugs():
    lights = getLights()
    plugs = {}
    for light in lights:
        normalized = mapPlug(lights[light], light)
        if normalized is not None:
            plugs[light] = normalized
    return plugs


def getNormalizedPlugs():
    plugs = getPlugs()
    normalizedPlugs = []
    for plug in plugs:
        normalizedPlugs.append(plugs[plug])
    return normalizedPlugs


def getPlug(id: int):
    plug = getLight(id)
    if plug is None or plug["config"]["archetype"] != "plug":
        return None
    return plug


def getNormalizedPlug(id: int):
    plug = getPlug(id)
    if plug is None:
        return None
    return mapPlug(plug, id)


def setLightState(id: int, state: HueLightState):
    user, host = config.get_hue_user(), config.get_hue_host()
    if host == "" or user == "":
        return None

    return requests.put(
        f"http://{host}/api/{user}/lights/{id}/state", json=state.to_dict())


def setLightStateNormalized(id: int, state: LightState):
    new_state = HueLightState.from_dict({})

    if state.color is not None:
        if state.color.hue is not None:
            new_state.hue = state.color.hue / 360 * 65535
        if state.color.saturation is not None:
            new_state.sat = state.color.saturation / 100 * 255

    if state.on is not None:
        new_state.on = state.on
    if state.brightness is not None:
        new_state.bri = state.brightness * 255

    return setLightState(id, new_state)


@router.patch("/config")
def set_config(new_config: HueConfig):
    config.hue = new_config
    return Response(status_code=200)


class UserResponse(BaseModel):
    username: str


@router.get("/init", responses={200: {"model": UserResponse}, 400: {"model": str}})
def hue_init():
    host = config.get_hue_host()
    if host == "":
        return Response(status_code=400, content="No host set")

    userRequest = requests.post(
        f"http://{host}/api", json={"devicetype": "my_hue_app#home api"})

    json = userRequest.json()[0]
    error = json.get("error")

    if error is not None and error.get("type") == 101:
        return Response(status_code=400, content="Link button not pressed")

    user = userRequest.json()[0].get("success").get("username")

    config.set_hue_user(user)

    return JSONResponse(status_code=200, content={"username": user})


@router.get("/lights", response_model=dict[str, HueLightResponse])
def get_lights():
    return JSONResponse(status_code=200, content=getLights())


@router.get("/lights/{id}", response_model=HueLightResponse)
def get_light(id: int):
    return JSONResponse(status_code=200, content=getLight(id))


@router.put("/lights/{id}/state", response_model=dict)
async def set_light_state(id: int, state: HueLightState):
    response = setLightState(id, state)

    try:
        light = getLight(id)
        if light is not None:
            await broadcast(WebSocketMessage(
                type="light",
                data=light,
            ))
    except:
        pass

    if response is None:
        return Response(status_code=400, content="No host or user set")

    if response.status_code == 200:
        return Response(status_code=200)

    return Response(status_code=400, content=response.json())


@router.get("/plugs", response_model=dict[str, HuePlugResponse])
def get_plugs():
    return JSONResponse(status_code=200, content=getPlugs())


@router.get("/plugs/{id}", response_model=HuePlugResponse)
def get_plug(id: int):
    plug = getPlug(id)
    if plug is None:
        return Response(status_code=404, content="Plug not found")

    return JSONResponse(status_code=200, content=plug)


@router.put("/plugs/{id}/state", response_model=dict)
async def set_plug_state(id: int, state: HuePlugState):
    response = setLightState(id, state)

    try:
        plug = getPlug(id)
        if plug is not None:
            await broadcast(WebSocketMessage(
                type="plug",
                data=plug,
            ))
    except:
        pass

    if response is None:
        return Response(status_code=400, content="No host or user set")

    if response.status_code == 200:
        return Response(status_code=200)

    return Response(status_code=400, content=response.json())
