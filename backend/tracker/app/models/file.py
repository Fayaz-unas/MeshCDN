from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Boolean,
    func
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class File(Base):
    """
    Represents a file registered in the SwarmCDN tracker.

    This model stores ONLY file metadata.
    It never stores the actual file or chunk data.

    Relationships:
        - One Peer can register many Files.
        - One File will have many Chunks (future).
    """

    __tablename__ = "files"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    file_hash = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    file_size = Column(
        BigInteger,
        nullable=False
    )

    chunk_size = Column(
        Integer,
        nullable=False
    )

    total_chunks = Column(
        Integer,
        nullable=False
    )

    mime_type = Column(
        String(100),
        nullable=True
    )

    created_by_peer_id = Column(
        BigInteger,
        ForeignKey("peers.id", ondelete="RESTRICT"),
        nullable=False
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    created_by = relationship(
    "Peer",
    back_populates="registered_files"
   )