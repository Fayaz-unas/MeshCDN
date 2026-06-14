from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI

from app.api.peer_routes import router as peer_router
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

app.include_router(peer_router)


@app.get("/")
def root():
    return {
        "service": "SwarmCDN Tracker",
        "status": "running"
    }