from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.peer import Peer
from app.repositories.peer_repository import PeerRepository


class PeerService:

    @staticmethod
    def register_peer(
        db: Session,
        peer_id: str,
        ip_address: str,
        port: int
    ):

        peer = PeerRepository.get_by_peer_id(
            db,
            peer_id
        )

        now = datetime.utcnow()

        if peer is None:

            peer = Peer(
                peer_id=peer_id,
                ip_address=ip_address,
                port=port,
                status="online",
                last_seen=now
            )

            return PeerRepository.create_peer(
                db,
                peer
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