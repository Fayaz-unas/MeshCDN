import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


class FileAPI:
    """
    Tracker File API Client.

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
    # Register File
    # ---------------------------------------------------------

    @classmethod
    def register_file(
        cls,
        *,
        file_hash: str,
        manifest_hash: str,
        file_name: str,
        file_size: int,
        chunk_size: int,
        total_chunks: int,
        peer_id: str,
        mime_type: str | None = None,
    ) -> dict[str, Any]:

        payload = {

            "file_hash": file_hash,

            "manifest_hash": manifest_hash,

            "file_name": file_name,

            "file_size": file_size,

            "chunk_size": chunk_size,

            "total_chunks": total_chunks,

            "mime_type": mime_type,

            "peer_id": peer_id,
        }

        response = cls._session.post(

            cls._url("/files"),

            json=payload,

            timeout=cls.DEFAULT_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    # ---------------------------------------------------------
    # Get All Files
    # ---------------------------------------------------------

    @classmethod
    def get_all_files(
        cls,
    ) -> list[dict[str, Any]]:

        response = cls._session.get(

            cls._url("/files"),

            timeout=cls.DEFAULT_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    # ---------------------------------------------------------
    # Get File
    # ---------------------------------------------------------

    @classmethod
    def get_file(
        cls,
        file_hash: str,
    ) -> dict[str, Any]:

        response = cls._session.get(

            cls._url(
                f"/files/{file_hash}"
            ),

            timeout=cls.DEFAULT_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    # ---------------------------------------------------------
    # Delete File
    # ---------------------------------------------------------

    @classmethod
    def delete_file(
        cls,
        file_hash: str,
    ) -> dict[str, Any]:

        response = cls._session.delete(

            cls._url(
                f"/files/{file_hash}"
            ),

            timeout=cls.DEFAULT_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()