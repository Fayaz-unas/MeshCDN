import base64
import hashlib
import logging

from services.chunk_storage_service import (
    ChunkStorageService
)

logger = logging.getLogger(
    __name__
)


class ChunkDataHandler:

    @staticmethod
    def handle(
        payload: dict
    ) -> bool:

        try:

            required_fields = [

                "file_hash",

                "chunk_index",

                "chunk_hash",

                "chunk_data"

            ]

            for field in required_fields:

                if field not in payload:

                    logger.warning(
                        f"Missing field: {field}"
                    )

                    return False

            file_hash = payload[
                "file_hash"
            ]

            chunk_index = payload[
                "chunk_index"
            ]

            expected_hash = payload[
                "chunk_hash"
            ]

            encoded_chunk = payload[
                "chunk_data"
            ]

            chunk_bytes = (
                base64.b64decode(
                    encoded_chunk
                )
            )

            calculated_hash = (
                hashlib.sha256(
                    chunk_bytes
                ).hexdigest()
            )

            if (
                calculated_hash
                !=
                expected_hash
            ):

                logger.warning(
                    "Chunk hash verification failed."
                )

                return False

            ChunkStorageService.save_chunk(

                file_hash=
                file_hash,

                chunk_index=
                chunk_index,

                data=
                chunk_bytes

            )

            logger.info(

                f"Chunk {chunk_index} "

                f"stored successfully."

            )

            return True

        except Exception:

            logger.exception(
                "Failed to process CHUNK_DATA."
            )

            return False