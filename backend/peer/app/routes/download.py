import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.download_service import DownloadService

router = APIRouter(prefix="/download", tags=["Download"])
logger = logging.getLogger(__name__)

class DownloadRequest(BaseModel):
    file_hash: str

@router.post("")
def download_file(request: DownloadRequest):
    """
    Download a file from the swarm.
    """
    logger.info(f"Received request to download file: {request.file_hash}")
    try:
        service = DownloadService()
        result = service.download(request.file_hash)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.exception("Failed to download file")
        raise HTTPException(status_code=500, detail=str(e))
