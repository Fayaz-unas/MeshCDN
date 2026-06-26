from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    func
)

from sqlalchemy.orm import relationship

from app.db.base import Base


class Peer(Base):
    __tablename__ = "peers"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    peer_id = Column(
        String(100),
        unique=True,
        nullable=False
    )

    installation_id = Column(
        String(100),
        unique=True,
        nullable=False
    )

    ip_address = Column(
        String(45),
        nullable=False
    )

    port = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(10),
        nullable=False,
        default="online"
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    last_seen = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    registered_files = relationship(
    "File",
    back_populates="created_by"
    )

    owned_files = relationship(
    "PeerFileState",
    back_populates="peer",
    cascade="all, delete-orphan",
    )