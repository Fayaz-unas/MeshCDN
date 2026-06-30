import logging
from fastapi import APIRouter, HTTPException

from services.shared_file_service import SharedFileService

router = APIRouter(tags=["Files"])
logger = logging.getLogger(__name__)

@router.get("/files")
def get_files():
    """
    Returns local shared/downloaded files.
    """
    logger.info("Received request to get files")
    try:
        service = SharedFileService()
        # TODO: call correct method on SharedFileService if get_all_files doesn't exist
        # Currently leaving as a stub to prevent runtime errors if method name differs
        files = [] 
        if hasattr(service, "get_all_files"):
            files = service.get_all_files()
        
        return {"status": "success", "data": files}
    except Exception as e:
        logger.exception("Failed to get files")
        raise HTTPException(status_code=500, detail=str(e))

# Adding an alias that the frontend might use
@router.get("/shared-files")
def get_shared_files():
    return get_files()

@router.post("/stop-sharing/{file_hash}")
def stop_sharing(file_hash: str):
    """
    Stop sharing a file.
    """
    logger.info(f"Received request to stop sharing file: {file_hash}")
    try:
        service = SharedFileService()
        if hasattr(service, "unregister_file"):
            service.unregister_file(file_hash)
            return {"status": "success"}
        else:
            return {"status": "error", "message": "Method not found"}
    except Exception as e:
        logger.exception("Failed to stop sharing file")
        raise HTTPException(status_code=500, detail=str(e))

