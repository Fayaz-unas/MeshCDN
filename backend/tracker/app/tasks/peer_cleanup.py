import asyncio

from app.db.database import SessionLocal
from app.services.peer_service import PeerService


async def cleanup_inactive_peers():

    while True:
        print("Cleaning up inactive peers...")

        db = SessionLocal()

        try:
            PeerService.mark_inactive_peers(db)

        finally:
            db.close()

        await asyncio.sleep(30)