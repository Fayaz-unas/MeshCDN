import logging
from fastapi import APIRouter

router = APIRouter(prefix="/statistics", tags=["Statistics"])
logger = logging.getLogger(__name__)

@router.get("")
def get_statistics():
    """
    Return available statistics.
    """
    logger.info("Received request for statistics")
    # TODO: Fetch actual statistics from a service if available
    return {
        "status": "success",
        "data": {
            "total_uploaded": 0,
            "total_downloaded": 0,
            "files_shared": 0,
            "storage_used": 0
        }
    }
