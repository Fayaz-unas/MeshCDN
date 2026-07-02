import json
from pathlib import Path


class SettingsService:

    @classmethod
    def get_settings_path(cls):
        import sys
        base_paths = [
            Path(__file__).resolve().parent.parent / "config/settings.json",
            Path("config/settings.json"),
            Path("app/config/settings.json")
        ]
        if hasattr(sys, "_MEIPASS"):
            base_paths.insert(0, Path(sys._MEIPASS) / "app/config/settings.json")
            base_paths.insert(0, Path(sys._MEIPASS) / "config/settings.json")
        for p in base_paths:
            if p.exists():
                return p
        return Path("config/settings.json")

    @classmethod
    def get_settings(cls):
        with open(cls.get_settings_path(), "r") as file:
            return json.load(file)

    @classmethod
    def get_peer_port(cls):
        return cls.get_settings()["peer_port"]

   

    @classmethod
    def get_heartbeat_interval(cls):
        return cls.get_settings()["heartbeat_interval"]