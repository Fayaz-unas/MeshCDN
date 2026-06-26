from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------
# File Information
# ---------------------------------------------------------

class SwarmFileInfo(BaseModel):
    """
    File metadata returned during swarm discovery.
    """

    file_hash: str
    manifest_hash: str

    file_name: str

    file_size: int

    chunk_size: int

    total_chunks: int

    mime_type: str


# ---------------------------------------------------------
# Swarm Statistics
# ---------------------------------------------------------

class SwarmStatistics(BaseModel):
    """
    Overall swarm information.
    """

    total_peers: int

    online_peers: int

    seeders: int

    leechers: int

    generated_at: datetime


# ---------------------------------------------------------
# Peer Information
# ---------------------------------------------------------

class SwarmPeer(BaseModel):
    """
    Peer returned during swarm discovery.
    """

    model_config = ConfigDict(from_attributes=True)

    peer_id: str

    ip_address: str

    port: int

    owned_chunk_count: int

    is_seeder: bool

    chunk_map: list[list[int]]

    last_seen: datetime


# ---------------------------------------------------------
# Swarm Discovery Response
# ---------------------------------------------------------

class SwarmDiscoveryResponse(BaseModel):
    """
    Complete swarm discovery response.
    """

    protocol_version: str

    file: SwarmFileInfo

    swarm: SwarmStatistics

    peers: list[SwarmPeer]