from __future__ import annotations

import logging
import time
import uuid

from networking.peer_client import PeerClient

from networking.protocol import (
    MessageTypes,
    Protocol,
)

from protocol_handlers.chunk_data_handler import (
    ChunkDataHandler,
)

logger = logging.getLogger(__name__)


class PeerDownloadService:
    """
    Downloads chunks from remote peers.

    Responsibilities
    ----------------
    - Establish connection
    - Send REQUEST_CHUNK
    - Receive response
    - Validate response
    - Store chunk
    - Retry transient failures

    This service downloads a single chunk.
    Download orchestration belongs to DownloadService.
    """

    MAX_RETRIES = 3

    RETRY_DELAY_SECONDS = 1

    @classmethod
    def download_chunk(
        cls,
        peer_host: str,
        peer_port: int,
        file_hash: str,
        chunk_index: int,
    ) -> bool:

        request_id = str(
            uuid.uuid4()
        )

        logger.info(

            "Downloading chunk %s from %s:%s",

            chunk_index,

            peer_host,

            peer_port,

        )

        for attempt in range(
            1,
            cls.MAX_RETRIES + 1,
        ):

            logger.debug(

                "Attempt %s/%s",

                attempt,

                cls.MAX_RETRIES,

            )

            client = PeerClient()

            try:

                client.connect(
                    peer_host,
                    peer_port,
                )

                cls._send_chunk_request(

                    client=client,

                    request_id=request_id,

                    file_hash=file_hash,

                    chunk_index=chunk_index,

                )

                response = (
                    client.receive_message()
                )

                message = (
                    Protocol.parse_message(
                        response
                    )
                )

                if not cls._handle_response(

                    message=message,

                    request_id=request_id,

                    file_hash=file_hash,

                    chunk_index=chunk_index,

                ):

                    raise RuntimeError(
                        "Chunk validation failed."
                    )

                logger.info(

                    "Chunk %s downloaded successfully.",

                    chunk_index,

                )

                return True

            except Exception:

                logger.exception(

                    "Attempt %s failed.",

                    attempt,

                )

                if (

                    attempt
                    <
                    cls.MAX_RETRIES

                ):

                    time.sleep(
                        cls.RETRY_DELAY_SECONDS
                    )

            finally:

                client.disconnect()

        logger.error(

            "Unable to download chunk %s.",

            chunk_index,

        )

        return False
    
    @staticmethod
    def _send_chunk_request(
        client: PeerClient,
        request_id: str,
        file_hash: str,
        chunk_index: int,
    ) -> None:
        """
        Send a REQUEST_CHUNK message to the remote peer.
        """

        request = Protocol.create_message(
            MessageTypes.REQUEST_CHUNK,
            {
                "request_id": request_id,
                "file_hash": file_hash,
                "chunk_index": chunk_index,
            },
        )

        logger.debug(
            "Sending REQUEST_CHUNK for chunk %s.",
            chunk_index,
        )

        client.send_message(request)

    @classmethod
    def _handle_response(
        cls,
        message: dict,
        request_id: str,
        file_hash: str,
        chunk_index: int,
    ) -> bool:
        """
        Process the peer response.
        """

        message_type = Protocol.get_type(message)
        payload = Protocol.get_payload(message)

        if message_type == MessageTypes.CHUNK_NOT_FOUND:

            logger.warning(
                "Peer reported chunk %s not found: %s",
                chunk_index,
                payload.get(
                    "reason",
                    "Unknown reason",
                ),
            )

            return False

        if message_type != MessageTypes.CHUNK_DATA:

            logger.error(
                "Unexpected response type: %s",
                message_type,
            )

            return False

        if not cls._validate_chunk(
            payload=payload,
            request_id=request_id,
            file_hash=file_hash,
            chunk_index=chunk_index,
        ):

            return False

        success = ChunkDataHandler.handle(
            payload
        )

        if not success:

            logger.error(
                "Failed to store chunk %s.",
                chunk_index,
            )

            return False

        return True

    @staticmethod
    def _validate_chunk(
        payload: dict,
        request_id: str,
        file_hash: str,
        chunk_index: int,
    ) -> bool:
        """
        Validate the received chunk payload before storing it.
        """

        if payload.get("request_id") != request_id:

            logger.error(
                "Request ID mismatch."
            )

            return False

        if payload.get("file_hash") != file_hash:

            logger.error(
                "File hash mismatch."
            )

            return False

        if payload.get("chunk_index") != chunk_index:

            logger.error(
                "Chunk index mismatch."
            )

            return False

        if "chunk_data" not in payload:

            logger.error(
                "Chunk data missing."
            )

            return False

        if payload["chunk_data"] is None:

            logger.error(
                "Chunk payload is empty."
            )

            return False

        return True