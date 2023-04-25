import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from .hue import getNormalizedLights as getHueLights, getNormalizedLight as getHueLight, setLightStateNormalized as setHueLightState, getNormalizedPlugs as getHuePlugs, getNormalizedPlug as getHuePlug

router = APIRouter(
    prefix="",
    tags=["main"],
    responses={404: {"description": "Not found"}},
)

mainConfig = {
}


def allLights():
    return [*getHueLights()]


def allPlugs():
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


def setLightState(id: str, state: dict):
    try:
        if id.startswith("hue-"):
            return setHueLightState(int(id.replace("hue-", "")), state)
        return JSONResponse(status_code=404, content={"error": "Light not found"})
    except ValueError:
        return JSONResponse(status_code=404, content={"error": "Light not found"})


def setPlugState(id: str, state: dict):
    try:
        if id.startswith("hue-"):
            return setHueLightState(int(id.replace("hue-", "")), state)
        return JSONResponse(status_code=404, content={"error": "Plug not found"})
    except ValueError:
        return JSONResponse(status_code=404, content={"error": "Plug not found"})


def loadConfig():
    try:
        with open("mainConfig.json", "r") as f:
            mainConfig.update(json.load(f))
    except FileNotFoundError:
        saveConfig()


def saveConfig():
    with open("mainConfig.json", "w") as f:
        json.dump(mainConfig, f)


loadConfig()


@router.get("/lights")
def get_lights():
    return JSONResponse(status_code=200, content=allLights())


@router.get("/lights/{id}")
def get_light(id: str):
    light = getLight(id)

    if light is None:
        return JSONResponse(status_code=404, content={"error": "Light not found"})
    return JSONResponse(status_code=200, content=light)


@router.put("/lights/{id}/state")
def set_light_state(id: str, state: dict):
    response = setLightState(id, state)

    light = getLight(id)

    if response.status_code == 200 and light is not None:
        return JSONResponse(status_code=200, content=light)

    if light is None:
        return JSONResponse(status_code=404, content={"error": "Light not found"})

    return response


@router.get("/plugs")
def get_plugs():
    return JSONResponse(status_code=200, content=allPlugs())


@router.get("/plugs/{id}")
def get_plug(id: str):
    plug = getPlug(id)

    if plug is None:
        return JSONResponse(status_code=404, content={"error": "Plug not found"})
    return JSONResponse(status_code=200, content=plug)


@router.put("/plugs/{id}/state")
def set_plug_state(id: str, state: dict):
    response = setPlugState(id, state)

    plug = getPlug(id)

    if response.status_code == 200 and plug is not None:
        return JSONResponse(status_code=200, content=plug)

    if plug is None:
        return JSONResponse(status_code=404, content={"error": "Plug not found"})

    return response
