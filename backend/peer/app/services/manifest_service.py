import json
import mimetypes
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from models.manifest import Manifest
from models.manifest_chunk import ManifestChunk

from services.hash_service import HashService


class ManifestService:
    """
    Handles creation, storage and loading of file manifests.
    """

    STORAGE_ROOT = Path("storage")

    MANIFEST_FILENAME = "manifest.json"

    @classmethod
    def create_manifest(
        cls,
        *,
        file_hash: str,
        file_name: str,
        file_size_bytes: int,
        chunk_size_bytes: int,
        chunks: list,
    ) -> Manifest:
        """
        Create a manifest from chunk metadata.
        """

        manifest_chunks = [

            ManifestChunk(
                chunk_index=chunk.chunk_index,
                chunk_hash=chunk.chunk_hash,
                chunk_size_bytes=chunk.chunk_size_bytes,
            )

            for chunk in chunks
        ]

        mime_type = (
            mimetypes.guess_type(file_name)[0]
            or "application/octet-stream"
        )

        manifest = {

            "file_hash": file_hash,

            "file_name": file_name,

            "file_size_bytes": file_size_bytes,

            "chunk_size_bytes": chunk_size_bytes,

            "total_chunks": len(manifest_chunks),

            "mime_type": mime_type,

            "created_at": datetime.utcnow().isoformat(),

            "chunks": [
                asdict(chunk)
                for chunk in manifest_chunks
            ],
        }

        manifest_hash = HashService.hash_bytes(
            json.dumps(
                manifest,
                sort_keys=True,
            ).encode()
        )

        return Manifest(

            manifest_hash=manifest_hash,

            file_hash=file_hash,

            file_name=file_name,

            file_size_bytes=file_size_bytes,

            chunk_size_bytes=chunk_size_bytes,

            total_chunks=len(manifest_chunks),

            mime_type=mime_type,

            created_at=datetime.fromisoformat(
                manifest["created_at"]
            ),

            chunks=manifest_chunks,
        )

    @classmethod
    def save_manifest(
        cls,
        manifest: Manifest,
    ) -> Path:
        """
        Save manifest to disk.
        """

        directory = (
            cls.STORAGE_ROOT
            /
            manifest.file_hash
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = (
            directory
            /
            cls.MANIFEST_FILENAME
        )

        data = asdict(
            manifest
        )

        data["created_at"] = (
            manifest.created_at.isoformat()
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
            )

        return path

    @classmethod
    def load_manifest(
        cls,
        file_hash: str,
    ) -> Manifest:
        """
        Load manifest from disk.
        """

        path = (
            cls.STORAGE_ROOT
            /
            file_hash
            /
            cls.MANIFEST_FILENAME
        )

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        chunks = [

            ManifestChunk(**chunk)

            for chunk in data["chunks"]
        ]

        return Manifest(

            manifest_hash=data["manifest_hash"],

            file_hash=data["file_hash"],

            file_name=data["file_name"],

            file_size_bytes=data["file_size_bytes"],

            chunk_size_bytes=data["chunk_size_bytes"],

            total_chunks=data["total_chunks"],

            mime_type=data["mime_type"],

            created_at=datetime.fromisoformat(
                data["created_at"]
            ),

            chunks=chunks,
        )