from pymongo import MongoClient, database
from pymongo.collection import Collection
from typing import Any, Optional
from api.auth_handler import hash_password

from api.consts import HueConfig, WledItem
from api.model import UserSchema


def get_db() -> database.Database:
    return MongoClient("mongodb://localhost:27017/").get_database("web")


class UserDatabase:
    db: database.Database
    users: Collection

    def __init__(self):
        self.db = get_db()
        self.users = self.db.get_collection("users")

    def add_user(self, user: UserSchema):
        user_dict = user.dict()
        user_dict["password"] = hash_password(user_dict["password"])
        self.users.insert_one(user_dict)

    def get_user(self, username: str) -> Optional[UserSchema]:
        user = self.users.find_one({"username": username})
        if user is None:
            return None
        return UserSchema(**user)

    def get_user_by_email(self, email: str) -> Optional[UserSchema]:
        user = self.users.find_one({"email": email})
        if user is None:
            return None
        return UserSchema(**user)

    def get_user_by_id(self, id: str) -> Optional[UserSchema]:
        user = self.users.find_one({"_id": id})
        if user is None:
            return None
        return UserSchema(**user)

    def delete_user(self, username: str):
        self.users.delete_one({"username": username})


class ConfigDatabase:
    db: database.Database
    config: Collection

    __default_hue_config = {
        "bridges": {},
        "current_bridge_index": 0
    }

    def __init__(self):
        self.db = get_db()
        self.config = self.db.get_collection("config")

    def get(self, key: str) -> Any:
        return self.config.find_one({"key": key})

    def set(self, key: str, value: Any):
        self.config.update_one(
            {"key": key}, {"$set": {"value": value}}, upsert=True)

    def delete(self, key: str):
        self.config.delete_one({"key": key})

    def __check_bridge(self, bridge_id: str) -> bool:
        if self.config.find_one({"key": "hue"}) is None:
            self.config.insert_one(
                {"key": "hue", "value": self.__default_hue_config})
        entry = self.config.find_one({"key": "hue"})
        if entry is None:
            entry = {"value": self.__default_hue_config}

        return entry["value"]["bridges"].get(bridge_id) is not None

    def __new_bridge_id(self) -> str:
        entry = self.config.find_one({"key": "hue"})
        if entry is None:
            entry = {"value": self.__default_hue_config}
            self.config.insert_one({"key": "hue", "value": entry["value"]})
        return str(entry["value"]["current_bridge_index"] + 1)

    def add_hue_bridge(self, ip: Optional[str] = None, user: Optional[str] = None) -> tuple[bool, str]:
        bridge_id = int(self.__new_bridge_id())

        while self.__check_bridge(str(bridge_id)):
            bridge_id += 1

        bridge_id = str(bridge_id)

        if not self.__check_bridge(bridge_id):
            entry = self.config.find_one({"key": "hue"})
            if entry is None or entry.get("value") is None:
                return (False, "")
            for bridge in entry["value"]["bridges"]:
                if entry["value"]["bridges"][bridge].get("ip") == ip:
                    return (False, "")
            entry["value"]["bridges"][bridge_id] = {}
            entry["value"]["current_bridge_index"] = int(bridge_id)
            if ip is not None:
                entry["value"]["bridges"][bridge_id]["ip"] = ip
            if user is not None:
                entry["value"]["bridges"][bridge_id]["user"] = user
            self.config.update_one({"key": "hue"}, {"$set": entry})
            return (True, bridge_id)

        return (False, "")

    def remove_hue_bridge(self, bridge_id: str) -> bool:
        if self.__check_bridge(bridge_id):
            entry = self.config.find_one({"key": "hue"})
            if entry is None or entry.get("value") is None:
                return False
            entry["value"]["bridges"].pop(bridge_id)
            self.config.update_one({"key": "hue"}, {"$set": entry})
            return True

        return False

    def get_hue_bridge(self, bridge_id: str) -> HueConfig:
        if self.__check_bridge(bridge_id):
            entry = self.config.find_one({"key": "hue"})
            if entry is None or entry.get("value") is None:
                return HueConfig.from_dict({})
            return HueConfig.from_dict({"host": entry["value"]["bridges"][bridge_id].get("ip"), "user": entry["value"]["bridges"][bridge_id].get("user")})

        return HueConfig.from_dict({})

    def get_hue_bridges(self) -> dict[str, HueConfig]:
        entry = self.config.find_one({"key": "hue"})
        if entry is None or entry.get("value") is None:
            return {}
        bridges = {}
        for i in entry["value"]["bridges"]:
            bridges[i] = HueConfig.from_dict(entry["value"]["bridges"][i])
        return bridges

    def set_hue_bridge(self, bridge_id: str, ip: Optional[str] = None, user: Optional[str] = None) -> bool:
        if self.__check_bridge(bridge_id):
            entry = self.config.find_one({"key": "hue"})
            if entry is None or entry.get("value") is None:
                return False
            if ip is not None:
                entry["value"]["bridges"][bridge_id]["ip"] = ip
            if user is not None:
                entry["value"]["bridges"][bridge_id]["user"] = user
            self.config.update_one({"key": "hue"}, {"$set": entry})
            return True

        return False

    def get_hue_bridge_host(self, bridge_id: str) -> str:
        return self.get_hue_bridge(bridge_id).host or ""

    def get_hue_bridge_user(self, bridge_id: str) -> str:
        return self.get_hue_bridge(bridge_id).user or ""

    def set_hue_bridge_host(self, bridge_id: str, ip: str):
        self.set_hue_bridge(bridge_id, ip=ip)

    def set_hue_bridge_user(self, bridge_id: str, user: str):
        self.set_hue_bridge(bridge_id, user=user)

    def add_wled(self, ip: str, name: str):
        if self.config.find_one({"key": "wled"}) is None:
            self.config.insert_one({"key": "wled", "value": {}})
        entry = self.config.find_one({"key": "wled"})
        if entry is None:
            entry = {"value": {}}
        if entry.get("value") is None:
            entry["value"] = {}
        if entry["value"].get("ips") is None:
            entry["value"]["ips"] = []

        if entry["value"]["ips"].count({"ip": ip, "name": name}) == 0:
            entry["value"]["ips"].append({"ip": ip, "name": name})

        self.config.update_one({"key": "wled"}, {"$set": entry})

    def remove_wled(self, ip: str) -> bool:
        if self.config.find_one({"key": "wled"}) is None:
            self.config.insert_one({"key": "wled", "value": {}})
        entry = self.config.find_one({"key": "wled"})
        if entry is None:
            entry = {"value": {}}
        if entry.get("value") is None:
            entry["value"] = {}
        if entry["value"].get("ips") is None:
            entry["value"]["ips"] = []

        for i in range(len(entry["value"]["ips"])):
            if entry["value"]["ips"][i]["ip"] == ip:
                entry["value"]["ips"].pop(i)
                self.config.update_one(
                    {"key": "wled"}, {"$set": entry})
                return True

        return False

    def get_wled(self, ip: str) -> WledItem | None:
        if self.config.find_one({"key": "wled"}) is None:
            self.config.insert_one({"key": "wled", "value": {}})
        entry = self.config.find_one({"key": "wled"})
        if entry is None:
            entry = {"value": {}}
        if entry.get("value") is None:
            entry["value"] = {}
        if entry["value"].get("ips") is None:
            entry["value"]["ips"] = []

        for i in entry["value"]["ips"]:
            if i["ip"] == ip:
                return WledItem.from_dict(i)
        return None

    def get_wleds(self) -> list[WledItem]:
        if self.config.find_one({"key": "wled"}) is None:
            self.config.insert_one({"key": "wled", "value": {}})
        entry = self.config.find_one({"key": "wled"})
        if entry is None:
            entry = {"value": {}}
        if entry.get("value") is None:
            entry["value"] = {}
        if entry["value"].get("ips") is None:
            entry["value"]["ips"] = []

        return [WledItem.from_dict(i) for i in entry["value"]["ips"]]


config_db = ConfigDatabase()
user_db = UserDatabase()
