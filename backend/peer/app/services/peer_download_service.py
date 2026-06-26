import logging
import uuid

from networking.peer_client import (
    PeerClient
)

from networking.protocol import (
    Protocol,
    MessageTypes
)

from protocol_handlers.chunk_data_handler import (
    ChunkDataHandler
)

logger = logging.getLogger(
    __name__
)


class PeerDownloadService:

    @staticmethod
    def download_chunk(
        host: str,
        port: int,
        file_hash: str,
        chunk_index: int
    ) -> bool:

        client = PeerClient()

        try:

            logger.info(
                f"Downloading chunk "
                f"{chunk_index} "
                f"from {host}:{port}"
            )

            client.connect(
                host,
                port
            )

            request = (
                Protocol.create_message(

                    MessageTypes.REQUEST_CHUNK,

                    {

                        "request_id":
                        str(
                            uuid.uuid4()
                        ),

                        "file_hash":
                        file_hash,

                        "chunk_index":
                        chunk_index

                    }

                )
            )

            client.send_message(
                request
            )

            response = (
                client.receive_message()
            )

            message = (
                Protocol.parse_message(
                    response
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

            if (
                message_type
                ==
                MessageTypes.CHUNK_NOT_FOUND
            ):

                logger.warning(
                    payload.get(
                        "reason",
                        "Chunk not found."
                    )
                )

                return False

            if (
                message_type
                !=
                MessageTypes.CHUNK_DATA
            ):

                logger.error(
                    f"Unexpected message: "
                    f"{message_type}"
                )

                return False

            success = (
                ChunkDataHandler.handle(
                    payload
                )
            )

            if success:

                logger.info(
                    f"Chunk {chunk_index} "
                    f"downloaded successfully."
                )

            return success

        except Exception:

            logger.exception(
                f"Failed to download "
                f"chunk {chunk_index}"
            )

            return False

        finally:

            client.disconnect()