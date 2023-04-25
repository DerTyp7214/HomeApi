import json
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
import requests

router = APIRouter(
    prefix="/hue",
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


def mapLight(light, id: int):
    if "colormode" not in light["state"]:
        return None

    return {
        "id": f"hue-{id}",
        "name": light["name"],
        "on": light["state"]["on"],
        "brightness": float(light["state"]["bri"]) / 100,
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
        "productid": light["productid"],
    }


def mapPlug(plug, id: int):
    if plug["config"]["archetype"] != "plug":
        return None

    return {
        "id": f"hue-{id}",
        "name": plug["name"],
        "on": plug["state"]["on"],
        "reachable": plug["state"]["reachable"],
        "type": plug["type"],
        "model": plug["modelid"],
        "manufacturer": plug["manufacturername"],
        "uniqueid": plug["uniqueid"],
        "swversion": plug["swversion"],
        "productid": plug["productid"],
    }


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


def setLightState(id: int, state: dict):
    return requests.put(
        f"http://{hueConfig['host']}/api/{hueConfig['user']}/lights/{id}/state", json=state)


def setLightStateNormalized(id: int, state: dict):
    new_state = {}
    if "on" in state:
        new_state["on"] = state["on"]
    if "brightness" in state:
        new_state["bri"] = int(state["brightness"] * 100)
    if "color" in state:
        if "hue" in state["color"]:
            new_state["hue"] = int(state["color"]["hue"] / 360 * 65535)
        if "saturation" in state["color"]:
            new_state["sat"] = int(state["color"]["saturation"] / 100 * 255)

    return setLightState(id, new_state)


@router.patch("/config")
def set_config(new_config: dict):
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
def set_light_state(id: int, state: dict):
    resopnse = setLightState(id, state)

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
def set_plug_state(id: int, state: dict):
    resopnse = setLightState(id, state)

    if resopnse.status_code == 200:
        return Response(status_code=200)

    return Response(status_code=400, content=resopnse.json())
