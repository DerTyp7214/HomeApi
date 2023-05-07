from pymongo import MongoClient, database
from pymongo.collection import Collection
from typing import Optional
from .auth_handler import hash_password, decodeJWT

from .consts import HueConfig, WledItem
from .model import UserSchema


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

    def config_db_by_token(self, token: str):
        email = (decodeJWT(token) or {}).get("email")
        if email is None:
            return None
        user = self.get_user_by_email(email)
        if user is None:
            return None
        return ConfigDatabase(self, user)

    def config_db(self, user: UserSchema):
        return ConfigDatabase(self, user)

    def __get_user__(self, user: UserSchema) -> dict | None:
        return self.users.find_one({"username": user.username})

    def __update_user__(self, user: UserSchema, data: dict):
        self.users.update_one({"username": user.username}, {"$set": data})


class ConfigDatabase:
    db: UserDatabase
    user: UserSchema

    def __init__(self, db: UserDatabase, user: UserSchema):
        self.db = db
        self.user = user

    def __user__(self) -> dict:
        return self.db.__get_user__(self.user) or {}

    def __check_bridge__(self, bridge_id: str) -> bool:
        bridges: list[dict] = self.__user__(
        )["settings"].get("hue_bridges", [])
        for bridge in bridges:
            if bridge["id"] == bridge_id:
                return True
        return False

    def __new_bridge_id__(self) -> str:
        user = self.__user__()
        current_index = user.get("settings", {}).get("hue_index", 0)
        return str(current_index + 1)

    def add_hue_bridge(self, ip: Optional[str] = None, user: Optional[str] = None) -> tuple[bool, str]:
        bridge_id = int(self.__new_bridge_id__())

        while self.__check_bridge__(str(bridge_id)):
            bridge_id += 1

        bridge_id = str(bridge_id)

        if not self.__check_bridge__(bridge_id):
            current_user_data = self.__user__()
            new_bridge = {"id": bridge_id}
            if ip is not None:
                new_bridge["ip"] = ip
            if user is not None:
                new_bridge["user"] = user
            if current_user_data.get("settings") is None:
                current_user_data["settings"] = {}
            if current_user_data["settings"].get("hue_bridges") is None:
                current_user_data["settings"]["hue_bridges"] = []
            current_user_data["settings"]["hue_bridges"].append(new_bridge)
            current_user_data["settings"]["hue_index"] = int(bridge_id)
            self.db.__update_user__(self.user, current_user_data)
            return (True, bridge_id)

        return (False, "")

    def remove_hue_bridge(self, bridge_id: str) -> bool:
        if self.__check_bridge__(bridge_id):
            current_user_data = self.__user__()
            current_user_data["settings"]["hue_bridges"] = [
                bridge for bridge in current_user_data["settings"]["hue_bridges"] if bridge["id"] != bridge_id]
            self.db.__update_user__(self.user, current_user_data)
            return True

        return False

    def get_hue_bridges(self) -> dict[str, HueConfig]:
        current_user_data = self.__user__()
        bridges = {}
        for bridge in current_user_data["settings"]["hue_bridges"]:
            bridges[bridge["id"]] = HueConfig.from_dict(bridge)
        return bridges

    def get_hue_bridge(self, bridge_id: str) -> HueConfig:
        bridges = self.get_hue_bridges()
        return bridges.get(bridge_id, HueConfig.from_dict({"id": bridge_id}))

    def set_hue_bridge(self, bridge_id: str, ip: Optional[str] = None, user: Optional[str] = None) -> bool:
        if self.__check_bridge__(bridge_id):
            current_user_data = self.__user__()
            for bridge in current_user_data["settings"]["hue_bridges"]:
                if bridge["id"] == bridge_id:
                    if ip is not None:
                        bridge["ip"] = ip
                    if user is not None:
                        bridge["user"] = user
            self.db.__update_user__(self.user, current_user_data)
            return True

        return False

    def get_hue_bridge_host(self, bridge_id: str) -> str:
        return self.get_hue_bridge(bridge_id).ip or ""

    def get_hue_bridge_user(self, bridge_id: str) -> str:
        return self.get_hue_bridge(bridge_id).user or ""

    def set_hue_bridge_host(self, bridge_id: str, ip: str):
        self.set_hue_bridge(bridge_id, ip=ip)

    def set_hue_bridge_user(self, bridge_id: str, user: str):
        self.set_hue_bridge(bridge_id, user=user)

    def add_wled(self, ip: str, name: str) -> bool:
        current_user_data = self.__user__()
        if current_user_data.get("settings") is None:
            current_user_data["settings"] = {}
        if current_user_data["settings"].get("wleds") is None:
            current_user_data["settings"]["wleds"] = []

        if current_user_data["settings"]["wleds"].count({"ip": ip, "name": name}) == 0:
            current_user_data["settings"]["wleds"].append(
                {"ip": ip, "name": name})

            self.db.__update_user__(self.user, current_user_data)
            return True

        return False

    def remove_wled(self, ip: str) -> bool:
        current_user_data = self.__user__()
        if current_user_data.get("settings") is None or current_user_data["settings"].get("wleds") is None:
            return False

        current_user_data["settings"]["wleds"] = [
            wled for wled in current_user_data["settings"]["wleds"] if wled["ip"] != ip]

        self.db.__update_user__(self.user, current_user_data)
        return True

    def get_wleds(self) -> list[WledItem]:
        current_user_data = self.__user__()
        if current_user_data.get("settings") is None or current_user_data["settings"].get("wleds") is None:
            return []

        return [WledItem.from_dict(wled) for wled in current_user_data["settings"]["wleds"]]

    def get_wled(self, ip: str) -> WledItem | None:
        return next((wled for wled in self.get_wleds() if wled.ip == ip), None)


user_db = UserDatabase()
