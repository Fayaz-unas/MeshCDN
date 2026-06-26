import socket
import struct


class PeerClient:

    def __init__(self):

        self.client = None

    def connect(
        self,
        host: str,
        port: int
    ):

        self.client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.client.connect(
            (
                host,
                port
            )
        )

        print(
            f"Connected to {host}:{port}"
        )

    def _receive_exact(
        self,
        size: int
    ) -> bytes:

        data = b""

        while len(data) < size:

            packet = self.client.recv(
                size - len(data)
            )

            if not packet:

                raise ConnectionError(
                    "Connection closed."
                )

            data += packet

        return data

    def send_message(
        self,
        message: str
    ):

        encoded = message.encode(
            "utf-8"
        )

        length = struct.pack(
            "!I",
            len(encoded)
        )

        self.client.sendall(
            length + encoded
        )

    def receive_message(
        self
    ) -> str:

        header = self._receive_exact(
            4
        )

        length = struct.unpack(
            "!I",
            header
        )[0]

        payload = self._receive_exact(
            length
        )

        return payload.decode(
            "utf-8"
        )

    def disconnect(
        self
    ):

        if self.client:

            self.client.close()

            self.client = None