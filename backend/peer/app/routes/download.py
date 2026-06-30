import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.download_service import DownloadService, ACTIVE_DOWNLOADS

router = APIRouter(prefix="/download", tags=["Download"])
logger = logging.getLogger(__name__)

@router.get("/progress/{file_hash}")
def get_download_progress(file_hash: str):
    """Get the current progress of an active download."""
    if file_hash in ACTIVE_DOWNLOADS:
        return {"status": "success", "data": ACTIVE_DOWNLOADS[file_hash]}
    return {"status": "success", "data": {"progress": 100, "status": "completed"}}

@router.post("/{file_hash}/pause")
def pause_download(file_hash: str):
    if file_hash in ACTIVE_DOWNLOADS:
        ACTIVE_DOWNLOADS[file_hash]["control"] = "pause"
        ACTIVE_DOWNLOADS[file_hash]["speed"] = 0 # reset speed to 0 when paused
    return {"status": "success"}

@router.post("/{file_hash}/resume")
def resume_download(file_hash: str):
    if file_hash in ACTIVE_DOWNLOADS:
        ACTIVE_DOWNLOADS[file_hash]["control"] = "running"
        ACTIVE_DOWNLOADS[file_hash]["last_chunk_time"] = __import__('time').time()
    return {"status": "success"}

@router.post("/{file_hash}/cancel")
def cancel_download(file_hash: str):
    if file_hash in ACTIVE_DOWNLOADS:
        ACTIVE_DOWNLOADS[file_hash]["control"] = "cancel"
    return {"status": "success"}

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

from fastapi.responses import FileResponse
import os
from pathlib import Path

@router.get("/serve")
def serve_downloaded_file(file_name: str):
    """
    Serve a downloaded file to the browser.
    """
    downloads_dir = Path("downloads")
    file_path = downloads_dir / file_name
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(
        path=file_path, 
        filename=file_name,
        media_type="application/octet-stream"
    )
