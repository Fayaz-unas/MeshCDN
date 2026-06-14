from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.peer import Peer


class PeerRepository:

    @staticmethod
    def get_by_peer_id(
        db: Session,
        peer_id: str
    ):
        return (
            db.query(Peer)
            .filter(Peer.peer_id == peer_id)
            .first()
        )

    @staticmethod
    def create_peer(
        db: Session,
        peer: Peer
    ):
        db.add(peer)
        db.commit()
        db.refresh(peer)

        return peer
    
    @staticmethod
    def update_peer(
    db: Session,
    peer: Peer
    ):
        db.commit()
        db.refresh(peer)

        return peer
    
    @staticmethod
    def get_all_peers(
        db: Session
    ):
        return db.query(Peer).all()
    

    @staticmethod
    def mark_inactive_peers(
        db: Session
    ):
        timeout = datetime.utcnow() - timedelta(seconds=60)
        
        (
            db.query(Peer)
            .filter(
                Peer.status == "online",
                Peer.last_seen < timeout
            ) 
            .update(
                {"status": "offline"},
                synchronize_session=False
            )
        
        )
        
        db.commit()
