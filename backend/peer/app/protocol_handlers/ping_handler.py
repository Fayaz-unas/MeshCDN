import logging

from networking.protocol import (
    Protocol,
    MessageTypes
)

logger = logging.getLogger(
    __name__
)


class PingHandler:

    @staticmethod
    def handle():

        logger.debug(
            "PING received"
        )

        return (
            Protocol.create_message(
                MessageTypes.PONG
            )
        )