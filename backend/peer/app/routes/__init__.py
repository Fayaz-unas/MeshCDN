from .share import router as share_router
from .download import router as download_router
from .dashboard import router as dashboard_router
from .files import router as files_router
from .peers import router as peers_router
from .transfers import router as transfers_router
from .statistics import router as statistics_router
from .settings import router as settings_router

__all__ = [
    "share_router",
    "download_router",
    "dashboard_router",
    "files_router",
    "peers_router",
    "transfers_router",
    "statistics_router",
    "settings_router"
]
