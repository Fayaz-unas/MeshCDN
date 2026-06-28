import logging
import time

from services.heartbeat_service import (
    HeartbeatService,
)
from services.peer_registration_service import (
    RegistrationService,
)
from services.peer_server_service import (
    PeerServerService,
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
        "Peer started successfully."
    )

    while True:

        time.sleep(
            1
        )


if __name__ == "__main__":

    main()