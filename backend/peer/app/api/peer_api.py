import requests
from dotenv import load_dotenv

import os

load_dotenv()
class PeerAPI:

    TRACKER_URL = os.getenv("TRACKER_URL")
    @classmethod
    def register_peer(
        cls,
        peer_id: str,
        port: int
    ):

        response = requests.post(
            f"{cls.TRACKER_URL}/register-peer",
            json={
                "peer_id": peer_id,
                "port": port
            }
        )

        response.raise_for_status()

        return response.json()