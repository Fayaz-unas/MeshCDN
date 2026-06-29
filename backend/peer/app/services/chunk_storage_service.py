from pathlib import Path
import logging
import shutil

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
    



    @classmethod
    def get_chunks_directory(
        cls,
        file_hash: str,
    ) -> Path:

        return (
            cls.get_file_directory(
                file_hash
            )
            /
            "chunks"
        )

    @classmethod
    def get_downloaded_chunk_count(
        cls,
        file_hash: str,
    ) -> int:

        chunks_directory = (
            cls.get_chunks_directory(
                file_hash
            )
        )

        if not chunks_directory.exists():

            return 0

        return len(
            list(
                chunks_directory.glob(
                    "*.chunk"
                )
            )
        )

    @classmethod
    def has_all_chunks(
        cls,
        file_hash: str,
        total_chunks: int,
    ) -> bool:

        return (

            cls.get_downloaded_chunk_count(
                file_hash
            )

            ==

            total_chunks

        )

    @classmethod
    def delete_partial_download(
        cls,
        file_hash: str,
    ) -> None:

        directory = (
            cls.get_file_directory(
                file_hash
            )
        )

        if directory.exists():

            shutil.rmtree(
                directory,
                ignore_errors=True,
            )

    @classmethod
    def get_storage_usage(
        cls,
        file_hash: str,
    ) -> int:

        directory = (
            cls.get_file_directory(
                file_hash
            )
        )

        if not directory.exists():

            return 0

        total = 0

        for file in directory.rglob("*"):

            if file.is_file():

                total += file.stat().st_size

        return total