import logging
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/peers", tags=["Peers"])
logger = logging.getLogger(__name__)

@router.get("")
def get_peers():
    """
    Returns online peers by communicating with the tracker.
    """
    logger.info("Received request to get peers")
    try:
        # TODO: Use existing tracker communication layer to fetch online peers
        peers = []
        return {"status": "success", "data": peers}
    except Exception as e:
        logger.exception("Failed to get peers")
        raise HTTPException(status_code=500, detail=str(e))
