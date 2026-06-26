import asyncio
import threading

from networking.peer_server import (
    PeerServer
)

from services.settings_service import (
    SettingsService
)

port = SettingsService.get_peer_port()


class PeerServerService:

    _server: PeerServer | None = None

    @classmethod
    def get_server(
        cls
    ) -> PeerServer | None:

        return cls._server

    @classmethod
    async def run_server(
        cls
    ):

        cls._server = (
            PeerServer()
        )

        await cls._server.start(
            "0.0.0.0",
            port
        )

    @classmethod
    def start(
        cls
    ):

        server_thread = threading.Thread(

            target=lambda:
            asyncio.run(
                cls.run_server()
            ),

            daemon=True

        )

        server_thread.start()