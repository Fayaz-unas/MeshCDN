import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["Settings"])
logger = logging.getLogger(__name__)

class SettingsUpdate(BaseModel):
    # TODO: Define settings fields when updating is supported
    pass

@router.get("")
def get_settings():
    """
    Return current configuration.
    """
    logger.info("Received request to get settings")
    try:
        service = SettingsService()
        # TODO: Fetch actual configuration from SettingsService
        settings = {}
        return {"status": "success", "data": settings}
    except Exception as e:
        logger.exception("Failed to get settings")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("")
def update_settings(settings: SettingsUpdate):
    """
    Update runtime configuration.
    """
    logger.info("Received request to update settings")
    try:
        # TODO: Update runtime configuration if already supported by SettingsService
        return {"status": "success", "message": "Settings update not yet supported"}
    except Exception as e:
        logger.exception("Failed to update settings")
        raise HTTPException(status_code=500, detail=str(e))
