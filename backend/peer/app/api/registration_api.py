import requests
from dotenv import load_dotenv
import os
load_dotenv()
TRACKER_URL = os.getenv("TRACKER_URL")


class RegistrationAPI:

    @classmethod
    def register_peer(
        cls,
        peer_id: str,
        port: int,
        installation_id: str
    ):

        response = requests.post(
            f"{TRACKER_URL}/register-peer",
            json={
                "peer_id": peer_id,
                "port": port,
                "installation_id": installation_id

            }
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Failed to register peer: {e}")
        return response.json()