import threading
import time

from api.heartbeat_api import HeartbeatAPI

from services.peer_identity_service import (
    PeerIdentityService
)


class HeartbeatService:

    HEARTBEAT_INTERVAL = 30

    @staticmethod
    def heartbeat_loop():

        identity = (
            PeerIdentityService
            .get_or_create_identity()
        )

        peer_id = identity["peer_id"]

        while True:

            try:

                HeartbeatAPI.send_heartbeat(
                    peer_id=peer_id
                )

                print(
                    f"Heartbeat sent: {peer_id}"
                )

            except Exception as error:

                print(
                    f"Heartbeat failed: {error}"
                )

            time.sleep(
                HeartbeatService.HEARTBEAT_INTERVAL
            )

    @staticmethod
    def start():

        heartbeat_thread = threading.Thread(
            target=HeartbeatService.heartbeat_loop,
            daemon=True
        )

        heartbeat_thread.start()