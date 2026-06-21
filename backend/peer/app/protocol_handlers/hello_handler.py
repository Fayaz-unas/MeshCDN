import logging

from networking.protocol import (
    Protocol,
    MessageTypes
)

logger = logging.getLogger(
    __name__
)


class HelloHandler:

    @staticmethod
    def handle(
        payload: dict,
        address: tuple,
        connection_manager
    ):

        peer_id = payload.get(
            "peer_id"
        )

        installation_id = payload.get(
            "installation_id"
        )

        if not peer_id:

            raise ValueError(
                "peer_id missing"
            )

        if not installation_id:

            raise ValueError(
                "installation_id missing"
            )

        logger.info(
            f"Peer ID: {peer_id}"
        )

        logger.info(
            f"Installation ID: "
            f"{installation_id}"
        )

        connection_manager.add_peer(
            peer_id=peer_id,
            installation_id=installation_id,
            address=address
        )

        logger.info(
            f"Connected Peers: "
            f"{connection_manager.get_all_peers()}"
        )

        response = (
            Protocol.create_message(
                MessageTypes.WELCOME
            )
        )

        return (
            peer_id,
            response
        )