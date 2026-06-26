import asyncio
import logging
import socket
import struct

from networking.protocol import (
    Protocol
)

from networking.connection_manager import (
    ConnectionManager
)

from protocol_handlers.message_handler import (
    MessageHandler
)

from services.chunk_service import (
    ChunkService
)

from services.file_service import (
    FileService
)

from services.hash_service import (
    HashService
)

from services.shared_file_service import (
    SharedFileService
)





logger = logging.getLogger(
    __name__
)


class PeerServer:

    def __init__(self):

        self.connection_manager = (
            ConnectionManager()
        )

        self.shared_file_service = (
            SharedFileService()
        )

    async def receive_message(
        self,
        reader: asyncio.StreamReader
    ) -> str:
        
        header = await reader.readexactly(4)

        message_length = struct.unpack(
            "!I",
            header
        )[0]

        payload = await reader.readexactly(
            message_length
        )

        return payload.decode(
        "utf-8"
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

                try:

                    raw_message = (
                        await self.receive_message(
                            reader
                        )
                    )

                except asyncio.IncompleteReadError:

                    logger.info(
                        "Client disconnected."
                    )

                    break

                try:

                    message = (
                        Protocol.parse_message(
                            raw_message
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
                            self.connection_manager,

                            shared_file_service=
                            self.shared_file_service
                        )
                    )

                    if peer_id:

                        connected_peer_id = (
                            peer_id
                        )

                    encoded = response.encode(
                        "utf-8"
                    )

                    writer.write(

                        struct.pack(
                            "!I",
                            len(encoded)
                        )

                        +

                        encoded

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

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        sock.bind(
            (
                host,
                port
            )
        )

        sock.listen(
            128
        )

        sock.setblocking(
            False
        )

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


    def share_file(
            self,
            file_path: str
        ) -> str:

        file_metadata = (
            FileService.register_file(
            file_path=
            file_path
            )
        )

        file_hash = (
            HashService.hash_file(
                file_metadata.file_path
            )
        )

        chunks = (
            ChunkService.create_chunks(
                file_metadata
            )
        )

        self.shared_file_service.register_file(
            file_hash=
            file_hash,

            file_metadata=
            file_metadata,

            chunks=
            chunks
        )

        return file_hash
