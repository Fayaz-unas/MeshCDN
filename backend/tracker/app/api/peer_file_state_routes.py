from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.peer_file_state_schema import (
    RegisterPeerFileStateRequest,
    UpdatePeerFileStateRequest,
)
from app.services.peer_file_state_service import (
    PeerFileStateService,
)

router = APIRouter(
    prefix="/peer-file-states",
    tags=["Peer File States"],
)


# ---------------------------------------------------------
# Register Ownership
# ---------------------------------------------------------

@router.post("/")
def register_peer_file_state(
    request: RegisterPeerFileStateRequest,
    db: Session = Depends(get_db),
):

    service = PeerFileStateService(db)

    return service.register(request)


# ---------------------------------------------------------
# Update Ownership
# ---------------------------------------------------------

@router.patch("/{peer_id}/{file_hash}")
def update_peer_file_state(
    peer_id: str,
    file_hash: str,
    request: UpdatePeerFileStateRequest,
    db: Session = Depends(get_db),
):

    service = PeerFileStateService(db)

    return service.update(
        peer_id,
        file_hash,
        request,
    )


# ---------------------------------------------------------
# Get Files Owned By Peer
# ---------------------------------------------------------

@router.get("/peer/{peer_id}")
def get_files_for_peer(
    peer_id: str,
    db: Session = Depends(get_db),
):

    service = PeerFileStateService(db)

    return service.get_files_for_peer(
        peer_id
    )


# ---------------------------------------------------------
# Get Peers Sharing File
# ---------------------------------------------------------

@router.get("/file/{file_hash}")
def get_peers_for_file(
    file_hash: str,
    db: Session = Depends(get_db),
):

    service = PeerFileStateService(db)

    return service.get_peers_for_file(
        file_hash
    )


# ---------------------------------------------------------
# Delete Ownership
# ---------------------------------------------------------

@router.delete("/{peer_id}/{file_hash}")
def delete_peer_file_state(
    peer_id: str,
    file_hash: str,
    db: Session = Depends(get_db),
):

    service = PeerFileStateService(db)

    service.delete(
        peer_id,
        file_hash,
    )

    return {
        "message": "Peer file state deleted successfully."
    }