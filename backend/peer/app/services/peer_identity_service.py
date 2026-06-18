import json
import uuid

from pathlib import Path


class PeerIdentityService:

    CONFIG_PATH = Path(
        "config/peer.json"
    )

    @staticmethod
    def generate_peer_id():

        return (
            f"peer_{uuid.uuid4().hex[:12]}"
        )

    @staticmethod
    def generate_installation_id():

        return uuid.uuid4().hex

    @classmethod
    def save_identity(
        cls,
        peer_id: str,
        installation_id: str
    ):

        cls.CONFIG_PATH.parent.mkdir(
            exist_ok=True
        )

        with open(
            cls.CONFIG_PATH,
            "w"
        ) as file:

            json.dump(
                {
                    "peer_id": peer_id,
                    "installation_id": (
                        installation_id
                    )
                },
                file,
                indent=4
            )

    @classmethod
    def load_identity(
        cls
    ):

        if not cls.CONFIG_PATH.exists():
            return None

        with open(
            cls.CONFIG_PATH,
            "r"
        ) as file:

            return json.load(
                file
            )

    @classmethod
    def get_or_create_identity(
        cls
    ):

        identity = (
            cls.load_identity()
        )

        if identity:
            return identity

        identity = {
            "peer_id": (
                cls.generate_peer_id()
            ),
            "installation_id": (
                cls.generate_installation_id()
            )
        }

        cls.save_identity(
            peer_id=identity[
                "peer_id"
            ],
            installation_id=identity[
                "installation_id"
            ]
        )

        return identity

    @classmethod
    def get_peer_id(
        cls
    ):

        identity = (
            cls.get_or_create_identity()
        )

        return identity[
            "peer_id"
        ]

    @classmethod
    def get_installation_id(
        cls
    ):

        identity = (
            cls.get_or_create_identity()
        )

        return identity[
            "installation_id"
        ]