import json
from pathlib import Path


class SettingsService:

    SETTINGS_PATH = Path("config/settings.json")

    @classmethod
    def get_settings(cls):

        with open(cls.SETTINGS_PATH, "r") as file:
            return json.load(file)

    @classmethod
    def get_peer_port(cls):
        return cls.get_settings()["peer_port"]

   

    @classmethod
    def get_heartbeat_interval(cls):
        return cls.get_settings()["heartbeat_interval"]