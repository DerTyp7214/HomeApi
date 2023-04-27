import json
from typing import Optional
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests

from api.consts import HueLightState, HuePlugState, LightColor, LightState, PlugState, WebSocketMessage, broadcast

router = APIRouter(
    tags=["hue"],
    responses={404: {"description": "Not found"}},
)

hueConfig = {
    "host": "",
}


def loadConfig():
    try:
        with open("hueConfig.json", "r") as f:
            hueConfig.update(json.load(f))
    except FileNotFoundError:
        saveConfig()


def saveConfig():
    with open("hueConfig.json", "w") as f:
        json.dump(hueConfig, f)


loadConfig()


class Config(BaseModel):
    host: Optional[str]
    user: Optional[str]


def mapLight(light, id: int):
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
    }

    if "productid" in light:
        light["productid"] = light["productid"]

    return light


def mapPlug(plug, id: int):
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
    }

    if "productid" in plug:
        new_plug["productid"] = plug["productid"]

    return new_plug


def getLights():
    lights = requests.get(
        f"http://{hueConfig['host']}/api/{hueConfig['user']}/lights")
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
    light = requests.get(
        f"http://{hueConfig['host']}/api/{hueConfig['user']}/lights/{id}")
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
    if plug["config"]["archetype"] != "plug":
        return None
    return plug


def getNormalizedPlug(id: int):
    plug = getPlug(id)
    if plug is None:
        return None
    return mapPlug(plug, id)


def setLightState(id: int, state: HueLightState):
    json = {}
    if state.on is not None:
        json["on"] = state.on
    if state.bri is not None:
        json["bri"] = int(state.bri)
    if state.hue is not None:
        json["hue"] = int(state.hue)
    if state.sat is not None:
        json["sat"] = int(state.sat)

    return requests.put(
        f"http://{hueConfig['host']}/api/{hueConfig['user']}/lights/{id}/state", json=json)


def setLightStateNormalized(id: int, state: LightState):
    new_state = HueLightState()

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
def set_config(new_config: Config):
    hueConfig.update(new_config)
    saveConfig()
    return Response(status_code=200)


@router.get("/init")
def hue_init():
    if hueConfig['host'] == "":
        return Response(status_code=400, content="No host set")

    userRequest = requests.post(
        f"http://{hueConfig['host']}/api", json={"devicetype": "my_hue_app#home api"})

    json = userRequest.json()[0]
    error = json.get("error")

    if error is not None and error.get("type") == 101:
        return Response(status_code=400, content="Link button not pressed")

    hueConfig['user'] = userRequest.json()[0].get("success").get("username")
    saveConfig()

    return JSONResponse(status_code=200, content={"username": hueConfig['user']})


@router.get("/lights")
def get_lights():
    return JSONResponse(status_code=200, content=getLights())


@router.get("/lights/{id}")
def get_light(id: int):
    return JSONResponse(status_code=200, content=getLight(id))


@router.put("/lights/{id}/state")
async def set_light_state(id: int, state: HueLightState):
    resopnse = setLightState(id, state)

    try:
        light = getLight(id)
        if light is not None:
            await broadcast(WebSocketMessage(
                type="light",
                data=light,
            ))
    except:
        pass

    if resopnse.status_code == 200:
        return Response(status_code=200)

    return Response(status_code=400, content=resopnse.json())


@router.get("/plugs")
def get_plugs():
    return JSONResponse(status_code=200, content=getPlugs())


@router.get("/plugs/{id}")
def get_plug(id: int):
    plug = getPlug(id)
    if plug is None:
        return Response(status_code=404, content="Plug not found")

    return JSONResponse(status_code=200, content=plug)


@router.put("/plugs/{id}/state")
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

    if response.status_code == 200:
        return Response(status_code=200)

    return Response(status_code=400, content=response.json())
