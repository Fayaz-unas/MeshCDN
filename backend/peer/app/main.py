import time
import logging
from pathlib import Path

from services.peer_registration_service import (
    RegistrationService
)

from services.heartbeat_service import (
    HeartbeatService
)

from services.peer_server_service import (
    PeerServerService
)

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - "
        "%(name)s - "
        "%(levelname)s - "
        "%(message)s"
    )
)


def main():

    response = (
        RegistrationService.register()
    )

    print(response)

    HeartbeatService.start()

    PeerServerService.start()

    #
    # Wait until the PeerServer
    # instance is created.
    #
    while (
        PeerServerService.get_server()
        is None
    ):

        time.sleep(
            0.1
        )

    server = (
        PeerServerService.get_server()
    )

    #
    # Development only.
    #
    # Automatically share a file
    # when the peer starts.
    #
    sample_file = (
        Path(__file__).parent
        / "test"
        / "sample.pdf"
    )

    if sample_file.exists():

        file_hash = (
            server.share_file(
                str(sample_file)
            )
        )

        print()

        print(
            "=" * 60
        )

        print(
            "Sample file shared"
        )

        print(
            f"File : {sample_file.name}"
        )

        print(
            f"Hash : {file_hash}"
        )

        print(
            "=" * 60
        )

    else:

        print()

        print(
            "=" * 60
        )

        print(
            "sample.pdf not found."
        )

        print(
            "Peer started without "
            "sharing any file."
        )

        print(
            "=" * 60
        )

    while True:

        time.sleep(
            1
        )


if __name__ == "__main__":

    main()