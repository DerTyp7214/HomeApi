from typing import Optional
from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
from api.auth_bearer import JWTBearer

from api.consts import ErrorResponse, HueConfig, HueLightResponse, HueLightState, HuePlugResponse, HuePlugState, Light, LightState, Plug, WebSocketMessage, broadcast
from api.db import user_db

router = APIRouter(
    tags=["hue"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(JWTBearer())]
)


class LightHandler:
    token: str

    def __init__(self, token: str):
        self.token = token

    def mapLight(self, bridge_id: str, light, id: int) -> Light | None:
        if "colormode" not in light["state"]:
            return None

        light = {
            "id": f"hue-{bridge_id}-{id}",
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

    def mapPlug(self, bridge_id: str, plug, id: int) -> Plug | None:
        if plug["config"]["archetype"] != "plug":
            return None

        new_plug = {
            "id": f"hue-{bridge_id}-{id}",
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

    def getLightsBride(self, bride_id: str):
        config = user_db.config_db_by_token(self.token)
        if config is None:
            return {}
        user, host = config.get_hue_bridge_user(
            bride_id), config.get_hue_bridge_host(bride_id)
        if host == "" or user == "":
            return {}
        lights = requests.get(
            f"http://{host}/api/{user}/lights")
        return lights.json()

    def __getLights__(self):
        config = user_db.config_db_by_token(self.token)
        if config is None:
            return {}
        bridges = config.get_hue_bridges()
        lights = {}
        for bridge in bridges:
            lights.update(self.getLightsBride(bridge))
        return lights

    def getLights(self):
        config = user_db.config_db_by_token(self.token)
        if config is None:
            return []
        bridges = config.get_hue_bridges()
        normalizedLights = []
        for bridge in bridges:
            lights = self.getLightsBride(bridge)
            for light in lights:
                normalized = self.mapLight(bridge, lights[light], light)
                if normalized is not None:
                    normalizedLights.append(normalized)
        return normalizedLights

    def __getLight__(self, bridge_id: str, id: int):
        config = user_db.config_db_by_token(self.token)
        if config is None:
            return None
        user, host = config.get_hue_bridge_user(
            bridge_id), config.get_hue_bridge_host(bridge_id)
        if host == "" or user == "":
            return None
        light = requests.get(
            f"http://{host}/api/{user}/lights/{id}")
        return light.json()

    def getLight(self, bridge_id: str, id: int):
        config = user_db.config_db_by_token(self.token)
        if config is None:
            return None
        light = self.__getLight__(bridge_id, id)
        normalizedLight = self.mapLight(bridge_id, light, id)
        return normalizedLight

    def getPlugsBride(self, bridge_id: str):
        lights = self.getLightsBride(bridge_id)
        plugs = {}
        for light in lights:
            if lights[light].get("config", {}).get("archetype") == "plug":
                plugs[light] = lights[light]
        return plugs

    def __getPlugs__(self):
        lights = self.__getLights__()
        plugs = {}
        for light in lights:
            if lights[light].get("config", {}).get("archetype") == "plug":
                plugs[light] = lights[light]
        return plugs

    def getPlugs(self):
        config = user_db.config_db_by_token(self.token)
        if config is None:
            return []
        bridges = config.get_hue_bridges()
        normalizedPlugs = []
        for bridge in bridges:
            plugs = self.getPlugsBride(bridge)
            for plug in plugs:
                normalized = self.mapPlug(bridge, plugs[plug], plug)
                if normalized is not None:
                    normalizedPlugs.append(normalized)
        return normalizedPlugs

    def __getPlug__(self, bridge_id: str, id: int):
        plug = self.__getLight__(bridge_id, id)
        if plug is None or plug["config"]["archetype"] != "plug":
            return None
        return plug

    def getPlug(self, bridge_id: str, id: int):
        plug = self.__getPlug__(bridge_id, id)
        if plug is None:
            return None
        return self.mapPlug(bridge_id, plug, id)

    def __setLightState__(self, bridge_id: str, id: int, state: HueLightState):
        config = user_db.config_db_by_token(self.token)
        if config is None:
            return None
        user, host = config.get_hue_bridge_user(
            bridge_id), config.get_hue_bridge_host(bridge_id)
        if host == "" or user == "":
            return None

        return requests.put(
            f"http://{host}/api/{user}/lights/{id}/state", json=state.to_dict())

    def setLightState(self, bridge_id: str, id: int, state: LightState):
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

        return self.__setLightState__(bridge_id, id, new_state)


class NewBridge(BaseModel):
    id: str


class HueBody(BaseModel):
    host: Optional[str]
    user: Optional[str]


@router.put("/config/add", responses={200: {"model": NewBridge}, 400: {"model": str}, 401: {"model": ErrorResponse}})
def set_config(new_config: HueBody, token: str = Depends(JWTBearer())):
    config = user_db.config_db_by_token(token)
    if config is None:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})

    success, id = config.add_hue_bridge(new_config.host, new_config.user)

    if success:
        return JSONResponse(status_code=200, content={"id": id})

    return Response(status_code=400, content="Bridge already added")


class UserResponse(BaseModel):
    username: str


@router.get("/init/{bridge_id}", responses={200: {"model": UserResponse}, 400: {"model": str}, 401: {"model": ErrorResponse}})
def hue_init(bridge_id: str, token: str = Depends(JWTBearer())):
    config = user_db.config_db_by_token(token)
    if config is None:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    host = config.get_hue_bridge_host(bridge_id)
    if host == "":
        return Response(status_code=400, content="No host set")

    userRequest = requests.post(
        f"http://{host}/api", json={"devicetype": "my_hue_app#home api"})

    json = userRequest.json()[0]
    error = json.get("error")

    if error is not None and error.get("type") == 101:
        return Response(status_code=400, content="Link button not pressed")

    user = userRequest.json()[0].get("success").get("username")

    config.set_hue_bridge_user(bridge_id, user)

    return JSONResponse(status_code=200, content={"username": user})


@router.delete("/config/{bridge_id}", responses={200: {"model": str}, 401: {"model": ErrorResponse}})
def delete_config(bridge_id: str, token: str = Depends(JWTBearer())):
    config = user_db.config_db_by_token(token)
    if config is None:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    if config.remove_hue_bridge(bridge_id):
        return Response(status_code=200)
    return Response(status_code=400)


@router.get("/lights", response_model=dict[str, HueLightResponse])
def get_lights(token: str = Depends(JWTBearer())):
    return JSONResponse(status_code=200, content=LightHandler(token).__getLights__())


@router.get("/lights/{bridge_id}", response_model=dict[str, HueLightResponse])
def get_lights_bridge(bridge_id: str, token: str = Depends(JWTBearer())):
    return JSONResponse(status_code=200, content=LightHandler(token).getLightsBride(bridge_id))


@router.get("/lights/{bridge_id}/{id}", response_model=HueLightResponse)
def get_light(bridge_id: str, id: int, token: str = Depends(JWTBearer())):
    return JSONResponse(status_code=200, content=LightHandler(token).__getLight__(bridge_id, id))


@router.put("/lights/{bridge_id}/{id}/state", response_model=dict)
async def set_light_state(bridge_id: str, id: int, state: HueLightState, token: str = Depends(JWTBearer())):
    light_handler = LightHandler(token)
    response = light_handler.__setLightState__(bridge_id, id, state)

    try:
        light = light_handler.__getLight__(bridge_id, id)
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
def get_plugs(token: str = Depends(JWTBearer())):
    return JSONResponse(status_code=200, content=LightHandler(token).__getPlugs__())


@router.get("/plugs/{bridge_id}", response_model=dict[str, HuePlugResponse])
def get_plugs_bridge(bridge_id: str, token: str = Depends(JWTBearer())):
    return JSONResponse(status_code=200, content=LightHandler(token).getPlugsBride(bridge_id))


@router.get("/plugs/{bridge_id}/{id}", response_model=HuePlugResponse)
def get_plug(bridge_id: str, id: int, token: str = Depends(JWTBearer())):
    plug = LightHandler(token).__getPlug__(bridge_id, id)
    if plug is None:
        return Response(status_code=404, content="Plug not found")

    return JSONResponse(status_code=200, content=plug.to_dict())


@router.put("/plugs/{bridge_id}/{id}/state", response_model=dict)
async def set_plug_state(bridge_id: str, id: int, state: HuePlugState, token: str = Depends(JWTBearer())):
    light_handler = LightHandler(token)
    response = light_handler.__setLightState__(bridge_id, id, state)

    try:
        plug = light_handler.__getPlug__(bridge_id, id)
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
