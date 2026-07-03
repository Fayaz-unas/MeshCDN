import base64
import hashlib
import logging

from networking.protocol import (
    MessageTypes,
    Protocol
)

from services.chunk_reader_service import (
    ChunkReaderService
)
from services.chunk_storage_service import (
    ChunkStorageService
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

            chunk_bytes = None
            chunk_hash = None
            chunk_size_bytes = 0

            if ChunkStorageService.chunk_exists(file_hash, chunk_index):
                chunk_bytes = ChunkStorageService.load_chunk(file_hash, chunk_index)
                chunk_hash = hashlib.sha256(chunk_bytes).hexdigest()
                chunk_size_bytes = len(chunk_bytes)
            else:
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

                manifest = shared_file.get("manifest")
                total_chunks = manifest.total_chunks if manifest else 0
                if total_chunks == 0 and shared_file.get("chunks"):
                    total_chunks = len(shared_file["chunks"])

                if chunk_index < 0 or (total_chunks > 0 and chunk_index >= total_chunks):

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

                file_metadata = shared_file.get("file_metadata")
                chunks = shared_file.get("chunks")
                if file_metadata and chunks and 0 <= chunk_index < len(chunks):
                    chunk = chunks[chunk_index]
                    chunk_bytes = ChunkReaderService.read_chunk(
                        file_path=file_metadata.file_path,
                        chunk=chunk
                    )
                    chunk_hash = chunk.chunk_hash
                    chunk_size_bytes = chunk.chunk_size_bytes

            if chunk_bytes is None:
                logger.warning(
                    f"Chunk {chunk_index} could not be loaded from storage or disk."
                )
                return Protocol.create_message(
                    MessageTypes.CHUNK_NOT_FOUND,
                    {
                        "request_id": request_id,
                        "file_hash": file_hash,
                        "chunk_index": chunk_index,
                        "reason": "Chunk not available."
                    }
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
                    chunk_index,

                    "chunk_hash":
                    chunk_hash,

                    "chunk_size_bytes":
                    chunk_size_bytes,

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