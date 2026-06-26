import base64
import logging

from networking.protocol import (
    MessageTypes,
    Protocol
)

from services.chunk_reader_service import (
    ChunkReaderService
)


logger = logging.getLogger(
    __name__
)


class RequestChunkHandler:

    @staticmethod
    def handle(
        payload: dict,
        shared_file_service
    ) -> str:

        try:

            file_hash = payload.get(
                "file_hash"
            )

            chunk_index = payload.get(
                "chunk_index"
            )

            request_id = payload.get(
                "request_id"
            )

            if (
                file_hash is None
                or
                chunk_index is None
                or
                request_id is None
            ):

                logger.warning(
                    "Invalid REQUEST_CHUNK payload."
                )

                return Protocol.create_message(

                    MessageTypes.CHUNK_NOT_FOUND,

                    {
                        "request_id": request_id,
                        "reason": "Invalid request."
                    }

                )

            shared_file = (
                shared_file_service.get_shared_file(
                    file_hash
                )
            )

            if shared_file is None:

                logger.warning(
                    f"Shared file not found: "
                    f"{file_hash}"
                )

                return Protocol.create_message(

                    MessageTypes.CHUNK_NOT_FOUND,

                    {
                        "request_id": request_id,
                        "file_hash": file_hash,
                        "chunk_index": chunk_index,
                        "reason": "File not shared."
                    }

                )

            file_metadata = (
                shared_file[
                    "file_metadata"
                ]
            )

            chunks = (
                shared_file[
                    "chunks"
                ]
            )

            if (
                chunk_index < 0
                or
                chunk_index >= len(chunks)
            ):

                logger.warning(
                    f"Chunk {chunk_index} "
                    f"does not exist."
                )

                return Protocol.create_message(

                    MessageTypes.CHUNK_NOT_FOUND,

                    {
                        "request_id": request_id,
                        "file_hash": file_hash,
                        "chunk_index": chunk_index,
                        "reason": "Chunk not found."
                    }

                )

            chunk = chunks[
                chunk_index
            ]

            chunk_bytes = (
                ChunkReaderService.read_chunk(

                    file_path=
                    file_metadata.file_path,

                    chunk=
                    chunk

                )
            )

            encoded_chunk = (
                base64.b64encode(
                    chunk_bytes
                ).decode(
                    "utf-8"
                )
            )

            logger.info(
                f"Sending chunk "
                f"{chunk_index}"
            )

            return Protocol.create_message(

                MessageTypes.CHUNK_DATA,

                {

                    "request_id":
                    request_id,

                    "file_hash":
                    file_hash,

                    "chunk_index":
                    chunk.chunk_index,

                    "chunk_hash":
                    chunk.chunk_hash,

                    "chunk_size_bytes":
                    chunk.chunk_size_bytes,

                    "chunk_data":
                    encoded_chunk

                }

            )

        except Exception:

            logger.exception(
                "Failed to process "
                "REQUEST_CHUNK."
            )

            return Protocol.create_message(

                MessageTypes.CHUNK_NOT_FOUND,

                {

                    "request_id":
                    payload.get(
                        "request_id"
                    ),

                    "reason":
                    "Internal server error."

                }

            )