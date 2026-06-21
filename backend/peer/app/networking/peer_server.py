import asyncio
import logging
import socket

from networking.protocol import (
    Protocol
)

from networking.connection_manager import (
    ConnectionManager
)

from protocol_handlers.message_handler import (
    MessageHandler
)

logger = logging.getLogger(
    __name__
)


class PeerServer:

    def __init__(self):

        self.connection_manager = (
            ConnectionManager()
        )

    async def handle_connection(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ):

        address = writer.get_extra_info(
            "peername"
        )

        logger.info(
            f"Incoming connection: "
            f"{address}"
        )

        connected_peer_id = None

        try:

            while True:

                data = await reader.read(
                    1024
                )

                if not data:

                    logger.info(
                        "Client closed "
                        "connection"
                    )

                    break

                try:

                    message = (
                        Protocol.parse_message(
                            data.decode()
                        )
                    )

                    message_type = (
                        Protocol.get_type(
                            message
                        )
                    )

                    payload = (
                        Protocol.get_payload(
                            message
                        )
                    )

                    peer_id, response = (
                        MessageHandler.handle(
                            message_type=
                            message_type,

                            payload=
                            payload,

                            address=
                            address,

                            connection_manager=
                            self.connection_manager
                        )
                    )

                    if peer_id:

                        connected_peer_id = (
                            peer_id
                        )

                    writer.write(
                        response.encode()
                    )

                    await writer.drain()

                except ValueError as e:

                    logger.warning(
                        f"Protocol Error: "
                        f"{e}"
                    )

                except KeyError as e:

                    logger.warning(
                        f"Missing Field: "
                        f"{e}"
                    )

        except Exception:

            logger.exception(
                "Connection error"
            )

        finally:

            logger.info(
                "Cleaning up connection"
            )

            writer.close()

            await writer.wait_closed()

            if connected_peer_id:

                self.connection_manager.remove_peer(
                    connected_peer_id
                )

            logger.info(
                f"Current Connections: "
                f"{self.connection_manager.get_all_peers()}"
            )

    async def start(
        self,
        host: str,
        port: int
    ):

        # Create a socket with SO_REUSEADDR to allow quick port reuse
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(128)
        sock.setblocking(False)

        server = (
            await asyncio.start_server(
                self.handle_connection,
                sock=sock
            )
        )

        logger.info(
            f"Peer server listening "
            f"on {host}:{port}"
        )

        async with server:

            await server.serve_forever()