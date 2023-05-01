from urllib.parse import unquote
from fastapi import APIRouter, Depends, Response
import requests
from api.auth_bearer import JWTBearer
from api.db import user_db
from api.consts import ErrorResponse, Light, LightState, Wled, WledItem, WledState
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


class LightHandler:
    token: str

    def __init__(self, token: str):
        self.token = token

    def __map_light__(self, light: WledReponseState) -> Light:
        colors = []
        if light.state is not None and light.state.seg is not None:
            for seg in light.state.seg:
                colors.append((seg.col[0], seg.col[1], seg.col[2]))

        return Light(
            id=light.ip,
            name=light.name,
            on=light.state.on is True,
            brightness=light.state.bri if light.state.bri is not None else 0,
            color=colors,
            reachable=True,
            type="Extended color light",
            model="LCT001",
            manufacturer="Philips",
            uniqueid=light.ip,
            swversion="1.0",
            productid=None
        )

    async def __allLights__(self) -> list[WledReponseState]:
        lights = []
        config = user_db.config_db_by_token(self.token)
        if config is None:
            return lights
        for light in config.get_wleds():
            lightResponse = self.__getLight__(light.ip)
            if lightResponse is not None:
                lights.append(lightResponse)

        return lights

    def __getLight__(self, ip: str) -> WledReponseState | None:
        config = user_db.config_db_by_token(self.token)
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

    def __setLightState__(self, ip: str, state: WledState):
        return requests.post(f"http://{ip}/json/state", json=state.to_dict())

    async def getLights(self):
        lights = []
        for light in await self.__allLights__():
            lights.append(self.__map_light__(light))
        return lights

    def getLight(self, id: str):
        light = self.__getLight__(id)
        if light is None:
            return None
        return self.__map_light__(light)

    def setLightState(self, id: str, state: LightState):
        light = self.__getLight__(id)
        if light is None:
            return None
        new_state = {}
        if state.color is not None:
            new_state["seg"] = []
            for color in state.color:
                new_state["seg"].append({
                    "col": [color[0], color[1], color[2]]
                })
        if state.on is not None:
            new_state["on"] = state.on
        if state.brightness is not None:
            new_state["bri"] = state.brightness
        return self.__setLightState__(id, WledState.from_dict(new_state))


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
    lights = await LightHandler(token).__allLights__()

    return JSONResponse(status_code=200, content=lights)


@router.get("/lights/{ip}", responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 200: {"model": WledReponseState}})
async def light(ip: str, token: str = Depends(JWTBearer())):
    light = LightHandler(token).__getLight__(ip)

    if light is None:
        return JSONResponse(status_code=404, content={"error": "Light not found"})
    return JSONResponse(status_code=200, content=light)


@router.put("/lights/{ip}/state", responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 200: {"model": WledReponseState}})
async def light_state(ip: str, state: WledState, token: str = Depends(JWTBearer())):
    light_handler = LightHandler(token)
    response = light_handler.__setLightState__(ip, state)

    light = light_handler.__getLight__(ip)

    if light is None:
        return JSONResponse(status_code=404, content={"error": "Light not found"})

    if response.status_code == 200:
        return JSONResponse(status_code=200, content=light)

    return response
