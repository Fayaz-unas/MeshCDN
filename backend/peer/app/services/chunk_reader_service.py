from pathlib import Path
import logging

from models.chunk_metadata import (
    ChunkMetadata
)

logger = logging.getLogger(
    __name__
)


class ChunkReaderService:

    @staticmethod
    def read_chunk(
        file_path: str,
        chunk: ChunkMetadata
    ) -> bytes:

        path = Path(
            file_path
        )

        if not path.exists():

            raise FileNotFoundError(
                f"File not found: "
                f"{file_path}"
            )

        if not path.is_file():

            raise ValueError(
                f"Not a file: "
                f"{file_path}"
            )

        try:

            with open(
                path,
                "rb"
            ) as file:

                file.seek(
                    chunk.chunk_offset
                )

                data = file.read(
                    chunk.chunk_size_bytes
                )

            if len(data) != (
                chunk.chunk_size_bytes
            ):

                raise IOError(
                    "Incomplete chunk read"
                )

            return data

        except Exception:

            logger.exception(
                "Failed to read chunk"
            )

            raise