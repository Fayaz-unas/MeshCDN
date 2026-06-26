from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI

from app.api.peer_routes import router as peer_router
from app.api.file_routes import router as file_router
from app.api.peer_file_state_routes import router as peer_file_state_router
from app.tasks.peer_cleanup import cleanup_inactive_peers


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(
        cleanup_inactive_peers()
    )

    yield

    task.cancel()


app = FastAPI(
    title="SwarmCDN Tracker",
    version="1.0.0",
    lifespan=lifespan
)

# -----------------------------
# Register Routers
# -----------------------------

app.include_router(peer_router)
app.include_router(file_router)
app.include_router(peer_file_state_router)

@app.get("/")
def root():
    return {
        "service": "SwarmCDN Tracker",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    """
    Basic health check endpoint.
    """

    return {
        "status": "healthy"
    }