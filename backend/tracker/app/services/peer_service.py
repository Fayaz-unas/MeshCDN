from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.peer import Peer
from app.repositories.peer_repository import PeerRepository


class PeerService:

    @staticmethod
    def register_peer(
        db: Session,
        peer_id: str,
        ip_address: str,
        port: int,
        installation_id: str
    ):

        peer = PeerRepository.get_by_peer_id(
            db,
            peer_id
        )

        now = datetime.utcnow()

        existing_installation = (
            PeerRepository.get_by_installation_id(
            db,
            installation_id
            )
        )

        if (
            existing_installation is not None
            and
            (
                peer is None
                or
                peer.installation_id != installation_id
            )
        ):
            raise HTTPException(
                status_code=403,
                detail="Installation ID already exists with a different peer ID"
                )

        if peer is None:

            peer = Peer(
                peer_id=peer_id,
                installation_id=installation_id,
                ip_address=ip_address,
                port=port,
                status="online",
                last_seen=now
            )

            return PeerRepository.create_peer(
                db,
                peer
            )
        

        if peer.installation_id != installation_id:
            raise HTTPException(
                status_code=403,
                detail="Peer ID already exists with a different installation ID"
            )

        peer.ip_address = ip_address
        peer.port = port
        peer.status = "online"
        peer.last_seen = now

        return PeerRepository.update_peer(
            db,
            peer
        )

    @staticmethod
    def get_all_peers(
        db: Session
    ):
        return PeerRepository.get_all_peers(db)
    
    @staticmethod
    def heartbeat(
    db: Session,
    peer_id: str
    ):
        peer = PeerRepository.get_by_peer_id(
        db,
        peer_id
         )
        if peer is None:
            return None

        peer.status = "online"
        peer.last_seen = datetime.utcnow()
        
        return PeerRepository.update_peer(
            db,
            peer
    )

    @staticmethod
    def mark_inactive_peers(
    db: Session
    ):
        PeerRepository.mark_inactive_peers(db)