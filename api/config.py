import json
import os
from typing import Any, Optional

from api.consts import BaseClass, HueConfig, WledConfig, WledItem


class Config(BaseClass):
    hue: HueConfig = HueConfig.from_dict({})
    wled: WledConfig = WledConfig.from_dict({})

    __fields_set__ = set()

    def __init__(self):
        self.load()

    def load(self):
        if not os.path.exists("config.json"):
            self.save()
            return
        try:
            with open("config.json") as f:
                data = json.load(f)
                self.load_from_dict(data)
        except:
            self.save()

    def save(self):
        with open("config.json", "w") as f:
            json.dump(self.to_dict(), f)

    def __setattr__(self, name, value):
        if isinstance(value, BaseClass):
            self.__dict__[name].update(value.to_dict())
        else:
            self.__dict__[name] = value
        self.save()

    def __delattr__(self, name):
        res = super().__delattr__(name)
        self.save()
        return res

    def set_hue(self, host: Optional[str] = None, user: Optional[str] = None):
        if self.__dict__.get("hue") is None:
            self.__dict__["hue"] = {}

        if host is not None:
            self.__dict__["hue"]["host"] = host
        if user is not None:
            self.__dict__["hue"]["user"] = user

        self.save()

    def get_hue(self) -> HueConfig:
        if self.__dict__.get("hue") is None:
            self.__dict__["hue"] = {}
        return HueConfig.from_dict(self.__dict__["hue"])

    def get_hue_host(self) -> str:
        if self.__dict__.get("hue") is None:
            self.__dict__["hue"] = {}

        return self.__dict__["hue"].get("host", "")

    def get_hue_user(self) -> str:
        if self.__dict__.get("hue") is None:
            self.__dict__["hue"] = {}

        return self.__dict__["hue"].get("user", "")

    def set_hue_host(self, host: str):
        if self.__dict__.get("hue") is None:
            self.__dict__["hue"] = {}

        self.__dict__["hue"]["host"] = host
        self.save()

    def set_hue_user(self, user: str):
        if self.__dict__.get("hue") is None:
            self.__dict__["hue"] = {}

        self.__dict__["hue"]["user"] = user
        self.save()

    def add_wled(self, ip: str, name: str):
        if self.__dict__.get("wled") is None:
            self.__dict__["wled"] = {
                "ips": []
            }
        if self.__dict__["wled"].get("ips") is None:
            self.__dict__["wled"]["ips"] = []

        if self.__dict__["wled"]["ips"].count({"ip": ip, "name": name}) == 0:
            self.__dict__["wled"]["ips"].append({"ip": ip, "name": name})

        self.save()

    def remove_wled(self, ip: str) -> bool:
        if self.__dict__.get("wled") is None:
            self.__dict__["wled"] = {
                "ips": []
            }
        if self.__dict__["wled"].get("ips") is None:
            self.__dict__["wled"]["ips"] = []

        for i in range(len(self.__dict__["wled"]["ips"])):
            if self.__dict__["wled"]["ips"][i]["ip"] == ip:
                self.__dict__["wled"]["ips"].pop(i)
                self.save()
                return True

        self.save()
        return False

    def get_wled(self, ip: str) -> WledItem | None:
        if self.__dict__.get("wled") is None:
            self.__dict__["wled"] = {
                "ips": []
            }
        if self.__dict__["wled"].get("ips") is None:
            self.__dict__["wled"]["ips"] = []

        for i in self.__dict__["wled"]["ips"]:
            if i["ip"] == ip:
                return WledItem.from_dict(i)
        return None

    def get_wleds(self) -> list[WledItem]:
        if self.__dict__.get("wled") is None:
            self.__dict__["wled"] = {
                "ips": []
            }
        if self.__dict__["wled"].get("ips") is None:
            self.__dict__["wled"]["ips"] = []

        return [WledItem.from_dict(i) for i in self.__dict__["wled"]["ips"]]


config = Config()
