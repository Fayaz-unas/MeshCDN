import threading
import time
import logging


from api.heartbeat_api import HeartbeatAPI

logger = logging.getLogger(__name__)

from services.peer_identity_service import (
    PeerIdentityService
)

from services.settings_service import SettingsService

HEARTBEAT_INTERVAL = SettingsService.get_heartbeat_interval()

class HeartbeatService:

    HEARTBEAT_INTERVAL = SettingsService.get_heartbeat_interval()

    @staticmethod
    def heartbeat_loop():
        """Main heartbeat loop that sends periodic heartbeats to tracker."""
        try:
            identity = (
                PeerIdentityService
                .get_or_create_identity()
            )
            peer_id = identity["peer_id"]
            logger.info(f"Heartbeat service initialized for peer: {peer_id}")

        except Exception as e:
            logger.critical(f"Failed to initialize heartbeat service - cannot get peer identity: {e}")
            return

        while True:
            try:
                HeartbeatAPI.send_heartbeat(
                    peer_id=peer_id
                )
                logger.debug(f"Heartbeat sent successfully: {peer_id}")

          
            except Exception as e:
                logger.error(f"Heartbeat failed with unexpected error: {e}")

            time.sleep(
                HeartbeatService.HEARTBEAT_INTERVAL
            )

    @staticmethod
    def start():
        """Start the heartbeat service in a background thread."""
        try:
            heartbeat_thread = threading.Thread(
                target=HeartbeatService.heartbeat_loop,
                daemon=True,
                name="HeartbeatThread"
            )
            heartbeat_thread.start()
            logger.info("Heartbeat service started successfully")

        except Exception as e:
            logger.critical(f"Failed to start heartbeat service thread: {e}")
            raise Exception(f"Cannot start heartbeat service: {e}")