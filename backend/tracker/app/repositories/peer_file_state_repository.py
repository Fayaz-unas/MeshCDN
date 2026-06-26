from sqlalchemy.orm import Session

from app.models.peer_file_state import PeerFileState


class PeerFileStateRepository:

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # Create
    # ---------------------------------------------------------

    def create(
        self,
        peer_file_state: PeerFileState,
    ) -> PeerFileState:

        self.db.add(peer_file_state)
        self.db.commit()
        self.db.refresh(peer_file_state)

        return peer_file_state

    # ---------------------------------------------------------
    # Read
    # ---------------------------------------------------------

    def get_by_id(
        self,
        state_id: int,
    ) -> PeerFileState | None:

        return (
            self.db.query(PeerFileState)
            .filter(PeerFileState.id == state_id)
            .first()
        )

    def get_by_peer_and_file(
        self,
        peer_id: int,
        file_id: int,
    ) -> PeerFileState | None:

        return (
            self.db.query(PeerFileState)
            .filter(
                PeerFileState.peer_id == peer_id,
                PeerFileState.file_id == file_id,
            )
            .first()
        )

    def get_by_peer_id(
        self,
        peer_id: int,
    ) -> list[PeerFileState]:

        return (
            self.db.query(PeerFileState)
            .filter(
                PeerFileState.peer_id == peer_id
            )
            .all()
        )

    def get_by_file_id(
        self,
        file_id: int,
    ) -> list[PeerFileState]:

        return (
            self.db.query(PeerFileState)
            .filter(
                PeerFileState.file_id == file_id
            )
            .all()
        )

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def update(
        self,
        peer_file_state: PeerFileState,
    ) -> PeerFileState:

        self.db.commit()
        self.db.refresh(peer_file_state)

        return peer_file_state

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def delete(
        self,
        peer_file_state: PeerFileState,
    ) -> None:

        self.db.delete(peer_file_state)
        self.db.commit()