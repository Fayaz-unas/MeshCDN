import requests


class DiscoveryAPI:

    BASE_URL = (
        "http://127.0.0.1:8000"
    )

    @classmethod
    def get_peers(cls):

        response = requests.get(
            f"{cls.BASE_URL}/peers"
        )

        response.raise_for_status()

        return response.json()
