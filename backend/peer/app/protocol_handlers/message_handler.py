from networking.protocol import (
    MessageTypes
)

from protocol_handlers.hello_handler import (
    HelloHandler
)

from protocol_handlers.ping_handler import (
    PingHandler
)

from protocol_handlers.request_chunk_handler import (
    RequestChunkHandler
)


class MessageHandler:

    @staticmethod
    def handle(
        message_type,
        payload,
        address,
        connection_manager,
        shared_file_service
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

        if (
            message_type
            ==
            MessageTypes.REQUEST_CHUNK
        ):

            return (
                None,

                RequestChunkHandler.handle(

                    payload=
                    payload,

                    shared_file_service=
                    shared_file_service

                )
            )

        raise ValueError(

            f"Unknown message type: "

            f"{message_type}"

        )