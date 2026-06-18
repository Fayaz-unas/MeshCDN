import time

from services.peer_registration_service import (
    RegistrationService
)

from services.heartbeat_service import (
    HeartbeatService
)

from services.peer_server_service import (
    PeerServerService
)


def main():

    response = (
        RegistrationService
        .register()
    )

    print(response)

    HeartbeatService.start()

    PeerServerService.start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()