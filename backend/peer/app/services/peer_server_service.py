import asyncio
import threading

from networking.peer_server import (
    PeerServer
)

from services.settings_service import SettingsService

port = SettingsService.get_peer_port()



class PeerServerService:

    @staticmethod
    async def run_server():

        server = PeerServer()

        await server.start(
            "0.0.0.0",
            port
        )

    @staticmethod
    def start():

        server_thread = threading.Thread(
            target=lambda: asyncio.run(
                PeerServerService.run_server()
            ),
            daemon=True
        )

        server_thread.start()