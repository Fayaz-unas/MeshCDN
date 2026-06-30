from pathlib import Path
import logging

from services.chunk_storage_service import (
    ChunkStorageService
)
import hashlib

from services.hash_service import (
    HashService
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

                    from services.download_service import ACTIVE_DOWNLOADS
                    import time
                    
                    # Handle pause/cancel during reconstruction
                    control = ACTIVE_DOWNLOADS.get(file_hash, {}).get("control", "running")
                    if control == "cancel":
                        logger.info(f"Reconstruction {file_hash} cancelled by user.")
                        raise RuntimeError("Download cancelled by user.")
                        
                    while ACTIVE_DOWNLOADS.get(file_hash, {}).get("control") == "pause":
                        time.sleep(0.5)

                    chunk_data = (
                        ChunkStorageService.load_chunk(
                            file_hash,
                            chunk_index
                        )
                    )

                    destination.write(
                        chunk_data
                    )
                    
                    # Update progress during reconstruction (we keep it at 100% or we can just say status is reconstructing)
                    if file_hash in ACTIVE_DOWNLOADS:
                        ACTIVE_DOWNLOADS[file_hash]["status"] = "reconstructing"
                        # We can track reconstruction progress if we want, but letting UI know status is enough
                        # ACTIVE_DOWNLOADS[file_hash]["progress"] = ((chunk_index + 1) / total_chunks) * 100

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


    @classmethod
    def reconstruct_to_downloads(
        cls,
        file_hash: str,
        total_chunks: int,
        file_name: str,
    ) -> Path:

        downloads = Path(
            "downloads"
        )

        downloads.mkdir(
            exist_ok=True
        )

        output = (
            downloads
            /
            file_name
        )

        return cls.reconstruct_file(

            file_hash=
            file_hash,

            total_chunks=
            total_chunks,

            output_path=
            str(output)

        )

    @classmethod
    def verify_integrity(
        cls,
        file_path: Path,
        expected_hash: str,
    ) -> bool:

        calculated = (
            HashService.hash_file(
                str(file_path)
            )
        )

        return (
            calculated
            ==
            expected_hash
        )