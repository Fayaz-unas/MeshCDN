from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    func
)

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
        default="Online"
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