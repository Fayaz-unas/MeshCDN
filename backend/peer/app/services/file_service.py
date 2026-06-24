import logging
from pathlib import Path

from models.file_metadata import (
    FileMetadata
)

logger = logging.getLogger(
    __name__
)


class FileService:

    @staticmethod
    def register_file(
        file_path: str
    ) -> FileMetadata:

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

            metadata = FileMetadata(
                file_name=
                path.name,

                file_path=
                str(
                    path.resolve()
                ),

                file_extension=
                path.suffix,

                file_size_bytes=
                path.stat().st_size
            )

            logger.info(
                f"Registered file: "
                f"{metadata.file_name}"
            )

            return metadata

        except OSError:

            logger.exception(
                "Failed to read file metadata"
            )

            raise