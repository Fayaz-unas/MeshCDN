from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.swarm_schema import SwarmDiscoveryResponse
from app.services.swarm_service import SwarmService

router = APIRouter(
    prefix="/swarms",
    tags=["Swarm Discovery"],
)


@router.get(
    "/{file_hash}",
    response_model=SwarmDiscoveryResponse,
)
def discover_swarm(
    file_hash: str,
    db: Session = Depends(get_db),
):
    service = SwarmService(db)

    return service.discover(file_hash)