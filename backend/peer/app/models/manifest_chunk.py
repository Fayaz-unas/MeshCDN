from dataclasses import dataclass


@dataclass(frozen=True)
class ManifestChunk:
    """
    Represents a single chunk entry inside a manifest.
    """

    chunk_index: int

    chunk_hash: str

    chunk_size_bytes: int