import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


class PeerFileStateAPI:
    """
    Tracker Peer File State API Client.

    Responsible only for communicating with the tracker.
    No business logic belongs here.
    """

    DEFAULT_TIMEOUT = 10

    _session = requests.Session()

    BASE_URL = os.getenv("TRACKER_URL")

    @classmethod
    def _url(
        cls,
        path: str,
    ) -> str:

        if not cls.BASE_URL:
            raise RuntimeError(
                "TRACKER_URL is not configured."
            )

        return f"{cls.BASE_URL}{path}"

    # ---------------------------------------------------------
    # Register Ownership
    # ---------------------------------------------------------

    @classmethod
    def register_peer_file_state(
        cls,
        *,
        peer_id: str,
        file_hash: str,
        chunk_map: list[list[int]],
        owned_chunk_count: int,
    ) -> dict[str, Any]:

        payload = {

            "peer_id": peer_id,

            "file_hash": file_hash,

            "chunk_map": chunk_map,

            "owned_chunk_count": owned_chunk_count,
        }

        response = cls._session.post(

            cls._url("/peer-file-states/"),

            json=payload,

            timeout=cls.DEFAULT_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    # ---------------------------------------------------------
    # Update Ownership
    # ---------------------------------------------------------

    @classmethod
    def update_peer_file_state(
        cls,
        *,
        peer_id: str,
        file_hash: str,
        chunk_map: list[list[int]],
        owned_chunk_count: int,
    ) -> dict[str, Any]:

        payload = {

            "chunk_map": chunk_map,

            "owned_chunk_count": owned_chunk_count,
        }

        response = cls._session.patch(

            cls._url(
                f"/peer-file-states/{peer_id}/{file_hash}"
            ),

            json=payload,

            timeout=cls.DEFAULT_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    # ---------------------------------------------------------
    # Get Files Owned By Peer
    # ---------------------------------------------------------

    @classmethod
    def get_files_for_peer(
        cls,
        peer_id: str,
    ) -> list[dict[str, Any]]:

        response = cls._session.get(

            cls._url(
                f"/peer-file-states/peer/{peer_id}"
            ),

            timeout=cls.DEFAULT_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    # ---------------------------------------------------------
    # Get Peers Sharing File
    # ---------------------------------------------------------

    @classmethod
    def get_peers_for_file(
        cls,
        file_hash: str,
    ) -> list[dict[str, Any]]:

        response = cls._session.get(

            cls._url(
                f"/peer-file-states/file/{file_hash}"
            ),

            timeout=cls.DEFAULT_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    # ---------------------------------------------------------
    # Delete Ownership
    # ---------------------------------------------------------

    @classmethod
    def delete_peer_file_state(
        cls,
        peer_id: str,
        file_hash: str,
    ) -> dict[str, Any]:

        response = cls._session.delete(

            cls._url(
                f"/peer-file-states/{peer_id}/{file_hash}"
            ),

            timeout=cls.DEFAULT_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()