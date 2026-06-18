from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.peer_schema import PeerRegistrationRequest
from app.services.peer_service import PeerService
from app.schemas.heartbeat_schema import HeartbeatRequest

router = APIRouter()


@router.post("/register-peer")
def register_peer(
    peer: PeerRegistrationRequest,
    request: Request,
    db: Session = Depends(get_db)
):

    peer_data = PeerService.register_peer(
        db=db,
        peer_id=peer.peer_id,
        installation_id=peer.installation_id,
        ip_address=request.client.host,
        port=peer.port
    )

    return {
        "message": "Peer registered successfully",
        "peer": peer_data
    }


@router.get("/peers")
def get_peers(
    db: Session = Depends(get_db)
):
    return PeerService.get_all_peers(db)  

@router.post("/heartbeat")
def heartbeat(
    heartbeat: HeartbeatRequest,
    db: Session = Depends(get_db)
):

    peer = PeerService.heartbeat(
        db,
        heartbeat.peer_id
    )

    if peer is None:
        return {
            "message": "Peer not found"
        }

    return {
        "message": "Heartbeat received"
    }
