from pathlib import Path
import logging

from services.chunk_storage_service import (
    ChunkStorageService
)

logger = logging.getLogger(
    __name__
)


class FileReconstructionService:

    BUFFER_SIZE = (
        1024 * 1024
    )

    @classmethod
    def reconstruct_file(
        cls,
        file_hash: str,
        total_chunks: int,
        output_path: str
    ) -> Path:

        output = Path(
            output_path
        )

        try:

            with open(
                output,
                "wb"
            ) as destination:

                for chunk_index in range(
                    total_chunks
                ):

                    chunk_data = (
                        ChunkStorageService.load_chunk(
                            file_hash,
                            chunk_index
                        )
                    )

                    destination.write(
                        chunk_data
                    )

            logger.info(
                f"File reconstructed: "
                f"{output.name}"
            )

            return output

        except Exception:

            logger.exception(
                "Failed to reconstruct file"
            )

            raise