from networking.protocol import (
    MessageTypes
)

from protocol_handlers.hello_handler import (
    HelloHandler
)

from protocol_handlers.ping_handler import (
    PingHandler
)


class MessageHandler:

    @staticmethod
    def handle(
        message_type,
        payload,
        address,
        connection_manager
    ):

        if (
            message_type
            ==
            MessageTypes.HELLO
        ):

            return (
                HelloHandler.handle(
                    payload=payload,
                    address=address,
                    connection_manager=
                    connection_manager
                )
            )

        if (
            message_type
            ==
            MessageTypes.PING
        ):

            return (
                None,
                PingHandler.handle()
            )

        raise ValueError(
            f"Unknown message type: "
            f"{message_type}"
        )