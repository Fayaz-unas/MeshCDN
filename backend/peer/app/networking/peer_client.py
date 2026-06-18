import socket


class PeerClient:

    def __init__(
        self
    ):
        self.client = None

    def connect(
        self,
        host: str,
        port: int
    ):

        self.client = socket.socket()

        self.client.connect(
            (
                host,
                port
            )
        )

        print(
            f"Connected to {host}:{port}"
        )

    def send_message(
        self,
        message: str
    ):

        self.client.send(
            message.encode()
        )

    def receive_message(
        self
    ):

        data = self.client.recv(
            1024
        )

        return data.decode()

    def disconnect(
        self
    ):

        if self.client:

            self.client.close()

            print(
                "Disconnected"
            )