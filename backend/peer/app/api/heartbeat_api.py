import requests
from dotenv import load_dotenv
import os

load_dotenv()
TRACKER_URL = os.getenv("TRACKER_URL")

class HeartbeatAPI:

    @classmethod
    def send_heartbeat(
        cls,
        peer_id: str
    ):

        response = requests.post(
            f"{TRACKER_URL}/heartbeat",
            json={
                "peer_id": peer_id
            }
        )

        response.raise_for_status()

        return response.json()