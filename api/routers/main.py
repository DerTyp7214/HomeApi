from api.auth_bearer import JWTBearer
from api.consts import Light, LightState, Plug, PlugState, WebSocketMessage, broadcast
from .hue import getNormalizedLights as getHueLights, getNormalizedLight as getHueLight, setLightStateNormalized as setHueLightState, getNormalizedPlugs as getHuePlugs, getNormalizedPlug as getHuePlug
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse


router = APIRouter(
    tags=["main"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(JWTBearer())]
)


def allLights(token: str) -> list[Light]:
    return [*getHueLights(token)]


def allPlugs(token: str) -> list[Plug]:
    return [*getHuePlugs(token)]


def getLight(token: str, id: str):
    try:
        if id.startswith("hue-"):
            bridge_id, light_id = id.replace("hue-", "").split("-")
            return getHueLight(token, bridge_id, int(light_id))
        return allLights(token)[int(id)]
    except ValueError:
        return None
    except IndexError:
        return None


def getPlug(token: str, id: str):
    try:
        if id.startswith("hue-"):
            bridge_id, plug_id = id.replace("hue-", "").split("-")
            return getHuePlug(token, bridge_id, int(plug_id))
        return allPlugs(token)[int(id)]
    except ValueError:
        return None
    except IndexError:
        return None


def setLightState(token: str, id: str, state: LightState):
    try:
        if id.startswith("hue-"):
            bridge_id, light_id = id.replace("hue-", "").split("-")
            response = setHueLightState(token, bridge_id, int(light_id), state)
            if response is None:
                return JSONResponse(status_code=404, content={"error": "Light not found"})
            return response
        return JSONResponse(status_code=404, content={"error": "Light not found"})
    except ValueError:
        return JSONResponse(status_code=404, content={"error": "Light not found"})


def setPlugState(token: str, id: str, state: PlugState):
    try:
        if id.startswith("hue-"):
            bridge_id, plug_id = id.replace("hue-", "").split("-")
            response = setHueLightState(token, bridge_id, int(plug_id), state)
            if response is None:
                return JSONResponse(status_code=404, content={"error": "Plug not found"})
            return response
        return JSONResponse(status_code=404, content={"error": "Plug not found"})
    except ValueError:
        return JSONResponse(status_code=404, content={"error": "Plug not found"})


@router.get("/lights", response_model=list[Light])
def get_lights(token: str = Depends(JWTBearer())):
    lights = []
    for light in allLights(token):
        lights.append(light.to_dict())

    return JSONResponse(status_code=200, content=lights)


@router.get("/lights/{id}", response_model=Light)
def get_light(id: str, token: str = Depends(JWTBearer())):
    light = getLight(token, id)

    if light is None:
        return JSONResponse(status_code=404, content={"error": "Light not found"})
    return JSONResponse(status_code=200, content=light.to_dict())


@router.put("/lights/{id}/state", response_model=dict)
async def set_light_state(id: str, state: LightState, token: str = Depends(JWTBearer())):
    response = setLightState(token, id, state)

    light = getLight(token, id)

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
def get_plugs(token: str = Depends(JWTBearer())):
    plugs = []
    for plug in allPlugs(token):
        plugs.append(plug.to_dict())

    return JSONResponse(status_code=200, content=plugs)


@router.get("/plugs/{id}", response_model=Plug)
def get_plug(id: str, token: str = Depends(JWTBearer())):
    plug = getPlug(token, id)

    if plug is None:
        return JSONResponse(status_code=404, content={"error": "Plug not found"})
    return JSONResponse(status_code=200, content=plug.to_dict())


@router.put("/plugs/{id}/state", response_model=dict)
async def set_plug_state(id: str, state: PlugState, token: str = Depends(JWTBearer())):
    response = setPlugState(token, id, state)

    plug = getPlug(token, id)

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
