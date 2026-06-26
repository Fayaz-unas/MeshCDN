from pathlib import Path
import logging


logger = logging.getLogger(
    __name__
)


class ChunkStorageService:

    STORAGE_ROOT = (
        Path("storage")
    )

    @classmethod
    def get_file_directory(
        cls,
        file_hash: str
    ) -> Path:

        return (
            cls.STORAGE_ROOT
            /
            file_hash
        )

    @classmethod
    def get_chunk_path(
        cls,
        file_hash: str,
        chunk_index: int
    ) -> Path:

        return (
            cls.get_file_directory(
                file_hash
            )
            /
            "chunks"
            /
            f"{chunk_index}.chunk"
        )

    @classmethod
    def save_chunk(
        cls,
        file_hash: str,
        chunk_index: int,
        data: bytes
    ) -> Path:

        chunk_path = (
            cls.get_chunk_path(
                file_hash,
                chunk_index
            )
        )

        chunk_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        try:

            with open(
                chunk_path,
                "wb"
            ) as file:

                file.write(
                    data
                )

            return chunk_path

        except Exception:

            logger.exception(
                "Failed to save chunk"
            )

            raise

    @classmethod
    def load_chunk(
        cls,
        file_hash: str,
        chunk_index: int
    ) -> bytes:

        chunk_path = (
            cls.get_chunk_path(
                file_hash,
                chunk_index
            )
        )

        if not chunk_path.exists():

            raise FileNotFoundError(
                f"Chunk not found: "
                f"{chunk_index}"
            )

        try:

            with open(
                chunk_path,
                "rb"
            ) as file:

                return file.read()

        except Exception:

            logger.exception(
                "Failed to load chunk"
            )

            raise

    @classmethod
    def chunk_exists(
        cls,
        file_hash: str,
        chunk_index: int
    ) -> bool:

        return (
            cls.get_chunk_path(
                file_hash,
                chunk_index
            ).exists()
        )