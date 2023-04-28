from pymongo import MongoClient, database
from pymongo.collection import Collection
import json
import os
from typing import Any, Optional

from api.consts import BaseClass, HueConfig, WledConfig, WledItem


def get_db() -> database.Database:
    return MongoClient("mongodb://localhost:27017/").get_database("web")


class ConfigDatabase:
    db: database.Database
    config: Collection

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

    def set_hue(self, host: Optional[str] = None, user: Optional[str] = None):
        if self.config.find_one({"key": "hue"}) is None:
            self.config.insert_one({"key": "hue", "value": {}})

        if host is not None:
            self.config.update_one(
                {"key": "hue"}, {"$set": {"value.host": host}})
        if user is not None:
            self.config.update_one(
                {"key": "hue"}, {"$set": {"value.user": user}})

    def get_hue(self) -> HueConfig:
        if self.config.find_one({"key": "hue"}) is None:
            self.config.insert_one({"key": "hue", "value": {}})
        entry = self.config.find_one({"key": "hue"})
        return HueConfig.from_dict((entry or {})["value"] or {})

    def get_hue_host(self) -> str:
        return self.get_hue().host or ""

    def get_hue_user(self) -> str:
        return self.get_hue().user or ""

    def set_hue_host(self, host: str):
        self.set_hue(host=host)

    def set_hue_user(self, user: str):
        self.set_hue(user=user)

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

        self.config.update_one({"key": "wled"}, {"$set": entry["value"]})

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
                    {"key": "wled"}, {"$set": entry["value"]})
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
