from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.chunking.chunk_map import ChunkMap
from app.models.peer_file_state import PeerFileState
from app.repositories.file_repository import FileRepository
from app.repositories.peer_file_state_repository import (
    PeerFileStateRepository,
)
from app.repositories.peer_repository import PeerRepository
from app.schemas.peer_file_state_schema import (
    RegisterPeerFileStateRequest,
    UpdatePeerFileStateRequest,
)


class PeerFileStateService:

    def __init__(self, db: Session):
        self.db = db
        self.peer_file_state_repository = PeerFileStateRepository(db)

    # ---------------------------------------------------------
    # Register Ownership
    # ---------------------------------------------------------

    def register(
        self,
        request: RegisterPeerFileStateRequest,
    ) -> PeerFileState:

        peer = PeerRepository.get_by_peer_id(
            self.db,
            request.peer_id,
        )

        if not peer:
            raise HTTPException(
                status_code=404,
                detail="Peer not found."
            )

        file = FileRepository.get_by_hash(
            self.db,
            request.file_hash,
        )

        if not file:
            raise HTTPException(
                status_code=404,
                detail="File not found."
            )

        existing = (
            self.peer_file_state_repository.get_by_peer_and_file(
                peer.id,
                file.id,
            )
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Peer already owns this file."
            )

        chunk_map = ChunkMap.deserialize(
            request.chunk_map
        )

        state = PeerFileState(
            peer_id=peer.id,
            file_id=file.id,
            chunk_map=chunk_map.serialize(),
            owned_chunk_count=chunk_map.count(),
        )

        return self.peer_file_state_repository.create(
            state
        )

    # ---------------------------------------------------------
    # Update Ownership
    # ---------------------------------------------------------

    def update(
        self,
        peer_id: str,
        file_hash: str,
        request: UpdatePeerFileStateRequest,
    ) -> PeerFileState:

        peer = PeerRepository.get_by_peer_id(
            self.db,
            peer_id,
        )

        if not peer:
            raise HTTPException(
                status_code=404,
                detail="Peer not found."
            )

        file = FileRepository.get_by_hash(
            self.db,
            file_hash,
        )

        if not file:
            raise HTTPException(
                status_code=404,
                detail="File not found."
            )

        state = (
            self.peer_file_state_repository.get_by_peer_and_file(
                peer.id,
                file.id,
            )
        )

        if not state:
            raise HTTPException(
                status_code=404,
                detail="Peer file state not found."
            )

        chunk_map = ChunkMap.deserialize(
            request.chunk_map
        )

        state.chunk_map = chunk_map.serialize()
        state.owned_chunk_count = chunk_map.count()

        return self.peer_file_state_repository.update(
            state
        )

    # ---------------------------------------------------------
    # Get Files Owned By Peer
    # ---------------------------------------------------------

    def get_files_for_peer(
        self,
        peer_id: str,
    ):

        peer = PeerRepository.get_by_peer_id(
            self.db,
            peer_id,
        )

        if not peer:
            raise HTTPException(
                status_code=404,
                detail="Peer not found."
            )

        return self.peer_file_state_repository.get_by_peer_id(
            peer.id
        )

    # ---------------------------------------------------------
    # Get Peers Sharing File
    # ---------------------------------------------------------

    def get_peers_for_file(
        self,
        file_hash: str,
    ):

        file = FileRepository.get_by_hash(
            self.db,
            file_hash,
        )

        if not file:
            raise HTTPException(
                status_code=404,
                detail="File not found."
            )

        return self.peer_file_state_repository.get_by_file_id(
            file.id
        )

    # ---------------------------------------------------------
    # Delete Ownership
    # ---------------------------------------------------------

    def delete(
        self,
        peer_id: str,
        file_hash: str,
    ) -> None:

        peer = PeerRepository.get_by_peer_id(
            self.db,
            peer_id,
        )

        if not peer:
            raise HTTPException(
                status_code=404,
                detail="Peer not found."
            )

        file = FileRepository.get_by_hash(
            self.db,
            file_hash,
        )

        if not file:
            raise HTTPException(
                status_code=404,
                detail="File not found."
            )

        state = (
            self.peer_file_state_repository.get_by_peer_and_file(
                peer.id,
                file.id,
            )
        )

        if not state:
            raise HTTPException(
                status_code=404,
                detail="Peer file state not found."
            )

        self.peer_file_state_repository.delete(
            state
        )