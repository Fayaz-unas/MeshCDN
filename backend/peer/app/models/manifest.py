from dataclasses import dataclass
from datetime import datetime

from models.manifest_chunk import (
    ManifestChunk,
)


@dataclass(frozen=True)
class Manifest:
    """
    Immutable manifest describing a shared file.

    The manifest contains everything required to verify
    and reconstruct a file on another peer.
    """

    file_hash: str

    manifest_hash: str

    file_name: str

    file_size_bytes: int

    chunk_size_bytes: int

    total_chunks: int

    mime_type: str

    created_at: datetime

    chunks: list[ManifestChunk]