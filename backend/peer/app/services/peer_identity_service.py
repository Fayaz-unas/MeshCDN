import json
import uuid
from pathlib import Path


class PeerIdentityService:

    CONFIG_PATH = Path("config/peer.json")

    @staticmethod
    def generate_peer_id():
        return f"peer_{uuid.uuid4().hex[:12]}"

    @classmethod
    def save_peer_id(
        cls,
        peer_id: str
    ):

        cls.CONFIG_PATH.parent.mkdir(
            exist_ok=True
        )

        with open(
            cls.CONFIG_PATH,
            "w"
        ) as file:

            json.dump(
                {"peer_id": peer_id},
                file,
                indent=4
            )

    @classmethod
    def load_peer_id(
        cls
    ):

        if not cls.CONFIG_PATH.exists():
            return None

        with open(
            cls.CONFIG_PATH,
            "r"
        ) as file:

            data = json.load(file)

        return data["peer_id"]

    @classmethod
    def get_or_create_peer_id(
        cls
    ):

        peer_id = cls.load_peer_id()

        if peer_id:
            return peer_id

        peer_id = cls.generate_peer_id()

        cls.save_peer_id(
            peer_id
        )

        return peer_id