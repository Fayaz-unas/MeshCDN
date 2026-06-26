from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RegisterPeerFileStateRequest(BaseModel):
    """
    Register a peer's ownership of a file.
    """

    peer_id: str
    file_hash: str

    chunk_map: list[list[int]] = Field(
        default_factory=list
    )

    owned_chunk_count: int = Field(
        ge=0
    )


class UpdatePeerFileStateRequest(BaseModel):
    """
    Update a peer's chunk ownership.
    """

    chunk_map: list[list[int]]

    owned_chunk_count: int = Field(
        ge=0
    )


class PeerFileStateResponse(BaseModel):
    """
    Peer ownership information.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    peer_id: str

    file_hash: str

    chunk_map: list[list[int]]

    owned_chunk_count: int

    updated_at: datetime


class PeerFileSummaryResponse(BaseModel):
    """
    Lightweight response used in swarm discovery.
    """

    peer_id: str

    chunk_map: list[list[int]]

    owned_chunk_count: int