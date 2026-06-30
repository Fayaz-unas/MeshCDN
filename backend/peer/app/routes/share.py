import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.share_service import ShareService

router = APIRouter(prefix="/share", tags=["Share"])
logger = logging.getLogger(__name__)

class ShareRequest(BaseModel):
    file_path: str

@router.post("")
def share_file(request: ShareRequest):
    """
    Share a local file with the network.
    """
    logger.info(f"Received request to share file: {request.file_path}")
    try:
        service = ShareService()
        result = service.share(request.file_path)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.exception("Failed to share file")
        raise HTTPException(status_code=500, detail=str(e))
