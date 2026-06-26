from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship

from app.db.base import Base


class PeerFileState(Base):
    """
    Represents a peer's ownership state for a specific file.

    Each row answers:

        "How much of this file does this peer currently own?"

    The actual chunks are stored as compressed intervals
    using ChunkMap serialization.

    Example:

        chunk_map = [
            [0, 500],
            [700, 900]
        ]

    One peer can own many files.

    One file can be owned by many peers.
    """

    __tablename__ = "peer_file_states"

    __table_args__ = (
        UniqueConstraint(
            "peer_id",
            "file_id",
            name="uq_peer_file_state",
        ),
        Index(
            "idx_peer_file_peer",
            "peer_id",
        ),
        Index(
            "idx_peer_file_file",
            "file_id",
        ),
    )

    # ---------------------------------------------------------
    # Primary Key
    # ---------------------------------------------------------

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------

    peer_id = Column(
        BigInteger,
        ForeignKey(
            "peers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    file_id = Column(
        BigInteger,
        ForeignKey(
            "files.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ---------------------------------------------------------
    # Ownership Information
    # ---------------------------------------------------------

    chunk_map = Column(
        MutableList.as_mutable(JSONB),
        nullable=False,
        default=list,
        comment="Serialized ChunkMap intervals.",
    )

    owned_chunk_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ---------------------------------------------------------
    # SQLAlchemy Relationships
    # ---------------------------------------------------------

    peer = relationship(
        "Peer",
        back_populates="owned_files",
    )

    file = relationship(
        "File",
        back_populates="owners",
    )