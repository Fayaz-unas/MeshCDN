from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.chunking.chunk_map import ChunkMap

from app.repositories.file_repository import FileRepository
from app.repositories.peer_file_state_repository import (
    PeerFileStateRepository,
)
from app.repositories.peer_repository import PeerRepository

from app.schemas.swarm_schema import (
    SwarmDiscoveryResponse,
    SwarmFileInfo,
    SwarmPeer,
    SwarmStatistics,
)


class SwarmService:
    """
    Coordinates swarm discovery.

    Responsibilities
    ----------------
    - Validate requested file
    - Discover peers
    - Calculate swarm statistics
    - Determine file availability
    - Build API response
    """

    PROTOCOL_VERSION = "1.0"

    def __init__(self, db: Session):

        self.db = db

        self.peer_file_state_repository = (
            PeerFileStateRepository(db)
        )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def discover(
        self,
        file_hash: str,
    ) -> SwarmDiscoveryResponse:

        # -------------------------------------------------
        # Find File
        # -------------------------------------------------

        file = FileRepository.get_by_hash(
            self.db,
            file_hash,
        )

        if file is None:
            raise HTTPException(
                status_code=404,
                detail="File not found.",
            )

        # -------------------------------------------------
        # Load Ownership Records
        # -------------------------------------------------

        peer_file_states = (
            self.peer_file_state_repository.get_by_file_id(
                file.id
            )
        )

        # -------------------------------------------------
        # File exists but nobody owns it
        # -------------------------------------------------

        if not peer_file_states:

            return SwarmDiscoveryResponse(

                protocol_version=self.PROTOCOL_VERSION,

                file=self._build_file(file),

                swarm=SwarmStatistics(

                    total_peers=0,

                    online_peers=0,

                    offline_peers=0,

                    seeders=0,

                    leechers=0,

                    file_available=False,

                    generated_at=datetime.utcnow(),

                ),

                peers=[],
            )

        # -------------------------------------------------
        # Calculate overall file availability
        # -------------------------------------------------

        combined_chunk_map = ChunkMap.merge_all(
            [
                ChunkMap.deserialize(
                    state.chunk_map
                )
                for state in peer_file_states
            ]
        )

        file_available = combined_chunk_map.is_complete(
            file.total_chunks
        )

        # -------------------------------------------------
        # Load Online Peers
        # -------------------------------------------------

        peer_ids = [
            state.peer_id
            for state in peer_file_states
        ]

        online_peers = PeerRepository.get_online_by_ids(
            self.db,
            peer_ids,
        )

        peer_lookup = {
            peer.id: peer
            for peer in online_peers
        }

        # -------------------------------------------------
        # Build Peer Response
        # -------------------------------------------------

        peers: list[SwarmPeer] = []

        online_seeders = 0

        for state in peer_file_states:

            peer = peer_lookup.get(
                state.peer_id
            )

            if peer is None:
                continue

            is_seeder = (
                state.owned_chunk_count
                == file.total_chunks
            )

            if is_seeder:
                online_seeders += 1

            peers.append(

                SwarmPeer(

                    peer_id=peer.peer_id,

                    ip_address=peer.ip_address,

                    port=peer.port,

                    owned_chunk_count=state.owned_chunk_count,

                    is_seeder=is_seeder,

                    chunk_map=state.chunk_map,

                    last_seen=peer.last_seen,
                )
            )
        # -------------------------------------------------
        # Swarm Statistics
        # -------------------------------------------------

        total_peers = len(peer_file_states)

        total_online_peers = len(peers)

        total_offline_peers = (
            total_peers - total_online_peers
        )

        online_leechers = (
            total_online_peers - online_seeders
        )

        swarm = SwarmStatistics(

            total_peers=total_peers,

            online_peers=total_online_peers,

            offline_peers=total_offline_peers,

            seeders=online_seeders,

            leechers=online_leechers,

            file_available=file_available,

            generated_at=datetime.utcnow(),
        )

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return SwarmDiscoveryResponse(

            protocol_version=self.PROTOCOL_VERSION,

            file=self._build_file(file),

            swarm=swarm,

            peers=peers,
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def _build_file(
        self,
        file,
    ) -> SwarmFileInfo:
        """
        Build the file metadata section of the response.
        """

        return SwarmFileInfo(

            file_hash=file.file_hash,

            manifest_hash=file.manifest_hash,

            file_name=file.file_name,

            file_size=file.file_size,

            chunk_size=file.chunk_size,

            total_chunks=file.total_chunks,

            mime_type=file.mime_type,
        )