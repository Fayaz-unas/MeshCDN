import logging
from fastapi import APIRouter

router = APIRouter(prefix="/transfers", tags=["Transfers"])
logger = logging.getLogger(__name__)

@router.get("")
def get_transfers():
    """
    Return active upload/download state.
    """
    logger.info("Received request for transfers state")
    # TODO: Implement transfer tracking in backend services
    # Return empty structure for now
    return {
        "status": "success",
        "data": {
            "downloads": [],
            "uploads": []
        }
    }
