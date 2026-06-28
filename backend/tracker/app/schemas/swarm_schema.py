from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------
# File Information
# ---------------------------------------------------------

class SwarmFileInfo(BaseModel):
    """
    Metadata describing the requested file.
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
    Overall swarm health and availability.
    """

    # Total peers that own this file
    total_peers: int

    # Peers currently online
    online_peers: int

    # Peers currently offline
    offline_peers: int

    # Online seeders
    seeders: int

    # Online leechers
    leechers: int

    # Can the file currently be reconstructed?
    file_available: bool

    # Response generation timestamp
    generated_at: datetime


# ---------------------------------------------------------
# Peer Information
# ---------------------------------------------------------

class SwarmPeer(BaseModel):
    """
    Information about an online peer participating
    in the swarm.
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