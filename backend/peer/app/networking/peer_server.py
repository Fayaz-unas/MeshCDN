import asyncio

from networking.protocol import (
    MessageTypes,
    Protocol
)

from networking.connection_manager import (
    ConnectionManager
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

        print(
            f"Incoming connection: {address}"
        )

        connected_peer_id = None

        try:

            while True:

                data = await reader.read(
                    1024
                )

                if not data:

                    print(
                        "Client closed connection"
                    )

                    break

                message = Protocol.parse_message(
                    data.decode()
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

                if message_type == MessageTypes.HELLO:

                    connected_peer_id = (
                        payload["peer_id"]
                    )

                    print(
                        f"Peer ID: "
                        f"{payload['peer_id']}"
                    )

                    print(
                        f"Installation ID: "
                        f"{payload['installation_id']}"
                    )

                    self.connection_manager.add_peer(
                        peer_id=payload[
                            "peer_id"
                        ],
                        installation_id=payload[
                            "installation_id"
                        ],
                        address=address
                    )

                    print(
                        "\nConnected Peers:"
                    )

                    print(
                        self.connection_manager
                        .get_all_peers()
                    )

                    writer.write(
                        Protocol.create_message(
                            MessageTypes.WELCOME
                        ).encode()
                    )

                    await writer.drain()

                elif message_type == MessageTypes.PING:

                    print(
                        "PING received"
                    )

                    writer.write(
                        Protocol.create_message(
                            MessageTypes.PONG
                        ).encode()
                    )

                    await writer.drain()

        except Exception as e:

            print(
                f"Connection Error: {e}"
            )

        finally:

            print(
                "\n=== FINALLY BLOCK REACHED ==="
            )

            writer.close()

            await writer.wait_closed()

            print(
                "Socket Closed"
            )

            if connected_peer_id:

                self.connection_manager.remove_peer(
                    connected_peer_id
                )

            print(
                "Current Connections:"
            )

            print(
                self.connection_manager
                .get_all_peers()
            )

    async def start(
        self,
        host: str,
        port: int
    ):

        server = await asyncio.start_server(
            self.handle_connection,
            host,
            port
        )

        print(
            f"Peer server listening on "
            f"{host}:{port}"
        )

        async with server:
            await server.serve_forever()