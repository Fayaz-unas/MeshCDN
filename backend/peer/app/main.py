import logging
import time
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.heartbeat_service import (
    HeartbeatService,
)
from services.peer_registration_service import (
    RegistrationService,
)
from services.peer_server_service import (
    PeerServerService,
)

from routes import (
    share_router,
    download_router,
    dashboard_router,
    files_router,
    peers_router,
    transfers_router,
    statistics_router,
    settings_router,
)

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - "
        "%(name)s - "
        "%(levelname)s - "
        "%(message)s"
    ),
)

app = FastAPI(title="MeshCDN Peer UI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(share_router)
app.include_router(download_router)
app.include_router(dashboard_router)
app.include_router(files_router)
app.include_router(peers_router)
app.include_router(transfers_router)
app.include_router(statistics_router)
app.include_router(settings_router)

@app.get("/status")
def status():
    return {"status": "online"}

def main():

    logging.info(
        "Starting MeshCDN Peer..."
    )

    response = (
        RegistrationService.register()
    )

    logging.info(response)

    HeartbeatService.start()

    PeerServerService.start()

    while (
        PeerServerService.get_server()
        is None
    ):

        time.sleep(
            0.1
        )

    logging.info(
        "Peer started successfully. Starting UI API server..."
    )

    uvicorn.run(app, host="0.0.0.0", port=5001)


if __name__ == "__main__":

    main()