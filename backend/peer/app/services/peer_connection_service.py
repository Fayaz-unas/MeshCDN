from networking.peer_client import (
    PeerClient
)

from networking.protocol import (
    Protocol,
    MessageTypes
)

from services.peer_identity_service import (
    PeerIdentityService
)


class PeerConnectionService:

    @staticmethod
    def connect_to_peer(
        peer: dict
    ):

        identity = (
            PeerIdentityService
            .get_or_create_identity()
        )

        client = PeerClient()

        client.connect(
            peer["ip_address"],
            peer["port"]
        )

        client.send_message(
            Protocol.create_message(
                MessageTypes.HELLO,
                {
                    "peer_id":
                        identity["peer_id"],

                    "installation_id":
                        identity[
                            "installation_id"
                        ]
                }
            )
        )

        response = (
            client.receive_message()
        )

        print(
            f"Connected to "
            f"{peer['peer_id']}"
        )

        print(response)

        client.disconnect()