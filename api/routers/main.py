from dataclasses import dataclass
from api.consts import Light, LightState, Plug, PlugState, WebSocketMessage, broadcast
from .hue import getNormalizedLights as getHueLights, getNormalizedLight as getHueLight, setLightStateNormalized as setHueLightState, getNormalizedPlugs as getHuePlugs, getNormalizedPlug as getHuePlug
import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse


router = APIRouter(
    tags=["main"],
    responses={404: {"description": "Not found"}},
)


def allLights() -> list[Light]:
    return [*getHueLights()]


def allPlugs() -> list[Plug]:
    return [*getHuePlugs()]


def getLight(id: str):
    try:
        if id.startswith("hue-"):
            return getHueLight(int(id.replace("hue-", "")))
        return allLights()[int(id)]
    except ValueError:
        return None
    except IndexError:
        return None


def getPlug(id: str):
    try:
        if id.startswith("hue-"):
            return getHuePlug(int(id.replace("hue-", "")))
        return allPlugs()[int(id)]
    except ValueError:
        return None
    except IndexError:
        return None


def setLightState(id: str, state: LightState):
    try:
        if id.startswith("hue-"):
            response = setHueLightState(int(id.replace("hue-", "")), state)
            if response is None:
                return JSONResponse(status_code=404, content={"error": "Light not found"})
            return response
        return JSONResponse(status_code=404, content={"error": "Light not found"})
    except ValueError:
        return JSONResponse(status_code=404, content={"error": "Light not found"})


def setPlugState(id: str, state: PlugState):
    try:
        if id.startswith("hue-"):
            response = setHueLightState(int(id.replace("hue-", "")), state)
            if response is None:
                return JSONResponse(status_code=404, content={"error": "Plug not found"})
            return response
        return JSONResponse(status_code=404, content={"error": "Plug not found"})
    except ValueError:
        return JSONResponse(status_code=404, content={"error": "Plug not found"})


def getPackageJson():
    with open("package.json", "r") as f:
        return json.load(f)


@dataclass
class StatusResponse():
    status: str
    version: str


@router.get("/status", response_model=StatusResponse)
def get_status():
    return JSONResponse(status_code=200, content={"status": "OK", "version": getPackageJson()["version"]})


@router.get("/lights", response_model=list[Light])
def get_lights():
    lights = []
    for light in allLights():
        lights.append(light.to_dict())

    return JSONResponse(status_code=200, content=lights)


@router.get("/lights/{id}", response_model=Light)
def get_light(id: str):
    light = getLight(id)

    if light is None:
        return JSONResponse(status_code=404, content={"error": "Light not found"})
    return JSONResponse(status_code=200, content=light.to_dict())


@router.put("/lights/{id}/state", response_model=dict)
async def set_light_state(id: str, state: LightState):
    response = setLightState(id, state)

    light = getLight(id)

    if light is None:
        return JSONResponse(status_code=404, content={"error": "Light not found"})

    try:
        await broadcast(WebSocketMessage.from_dict({
            "type": "light",
            "data": light.__dict__,
        }))
    except:
        pass

    if response.status_code == 200:
        return JSONResponse(status_code=200, content=light.to_dict())

    return response


@router.get("/plugs", response_model=list[Plug])
def get_plugs():
    plugs = []
    for plug in allPlugs():
        plugs.append(plug.to_dict())

    return JSONResponse(status_code=200, content=plugs)


@router.get("/plugs/{id}", response_model=Plug)
def get_plug(id: str):
    plug = getPlug(id)

    if plug is None:
        return JSONResponse(status_code=404, content={"error": "Plug not found"})
    return JSONResponse(status_code=200, content=plug.to_dict())


@router.put("/plugs/{id}/state", response_model=dict)
async def set_plug_state(id: str, state: PlugState):
    response = setPlugState(id, state)

    plug = getPlug(id)

    if plug is None:
        return JSONResponse(status_code=404, content={"error": "Plug not found"})

    try:
        await broadcast(WebSocketMessage(
            type="plug",
            data=plug.__dict__,
        ))
    except:
        pass

    if response.status_code == 200:
        return JSONResponse(status_code=200, content=plug.to_dict())

    return response
