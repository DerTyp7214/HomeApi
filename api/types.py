from typing import Optional
from pydantic import BaseModel


class LightColor(BaseModel):
    hue: Optional[float] = None
    saturation: Optional[float] = None


class LightState(BaseModel):
    on: Optional[bool] = None
    brightness: Optional[float] = None
    color: Optional[LightColor] = None


class HueLightState(BaseModel):
    on: Optional[bool] = None
    bri: Optional[float] = None
    hue: Optional[float] = None
    sat: Optional[float] = None


class PlugState(LightState):
    on: bool


class HuePlugState(HueLightState):
    on: bool
