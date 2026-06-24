from dataclasses import dataclass


@dataclass
class ChunkMetadata:

    chunk_index: int

    chunk_offset: int

    chunk_size_bytes: int

    chunk_hash: str