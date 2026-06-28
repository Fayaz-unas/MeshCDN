import os

import requests
from dotenv import load_dotenv

load_dotenv()


class DiscoveryAPI:
    """
    Client for the Tracker Swarm Discovery API.
    """

    BASE_URL = os.getenv("TRACKER_URL")

    @classmethod
    def discover_swarm(
        cls,
        file_hash: str,
    ) -> dict:
        """
        Discover the swarm for a specific file.

        Returns the complete Swarm Discovery response
        from the tracker.
        """

        response = requests.get(
            f"{cls.BASE_URL}/swarms/{file_hash}"
        )

        response.raise_for_status()

        return response.json()