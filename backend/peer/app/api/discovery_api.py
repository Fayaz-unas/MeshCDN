import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("TRACKER_URL")

class DiscoveryAPI:

    
    @classmethod
    def get_peers(cls):

        response = requests.get(
            f"{cls.BASE_URL}/peers"
        )

        response.raise_for_status()

        return response.json()
