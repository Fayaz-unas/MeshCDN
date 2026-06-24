import logging
from math import ceil

from models.file_metadata import (
    FileMetadata
)

from models.chunk_metadata import (
    ChunkMetadata
)

from services.hash_service import (
    HashService
)

logger = logging.getLogger(
    __name__
)


class ChunkService:

    CHUNK_SIZE_BYTES = (
        1024 * 1024
    )

    @classmethod
    def create_chunks(
        cls,
        file_metadata: FileMetadata
    ) -> list[ChunkMetadata]:

        if (
            file_metadata.file_size_bytes
            <= 0
        ):

            raise ValueError(
                "File size must be "
                "greater than zero"
            )

        total_chunks = ceil(
            file_metadata.file_size_bytes
            /
            cls.CHUNK_SIZE_BYTES
        )

        logger.info(
            f"Generating "
            f"{total_chunks} chunks"
        )

        chunks = []

        try:

            with open(
                file_metadata.file_path,
                "rb"
            ) as file:

                for chunk_index in range(
                    total_chunks
                ):

                    chunk_offset = (
                        chunk_index
                        *
                        cls.CHUNK_SIZE_BYTES
                    )

                    chunk_data = file.read(
                        cls.CHUNK_SIZE_BYTES
                    )

                    if not chunk_data:

                        break

                    chunk_size = len(
                        chunk_data
                    )

                    chunk_hash = (
                        HashService.hash_bytes(
                            chunk_data
                        )
                    )

                    chunk = ChunkMetadata(
                        chunk_index=
                        chunk_index,

                        chunk_offset=
                        chunk_offset,

                        chunk_size_bytes=
                        chunk_size,

                        chunk_hash=
                        chunk_hash
                    )

                    chunks.append(
                        chunk
                    )

            logger.info(
                f"Created "
                f"{len(chunks)} chunks"
            )

            return chunks

        except PermissionError:

            logger.exception(
                "Permission denied "
                "while chunking file"
            )

            raise

        except OSError:

            logger.exception(
                "OS error while "
                "creating chunks"
            )

            raise

        except Exception:

            logger.exception(
                "Unexpected chunking error"
            )

            raise