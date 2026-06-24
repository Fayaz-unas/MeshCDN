import hashlib
import logging
from pathlib import Path


logger = logging.getLogger(
    __name__
)


class HashService:

    HASH_ALGORITHM = (
        "sha256"
    )

    BUFFER_SIZE = (
        1024 * 1024
    )

    @classmethod
    def hash_bytes(
        cls,
        data: bytes
    ) -> str:

        if not isinstance(
            data,
            bytes
        ):

            raise TypeError(
                "data must be bytes"
            )

        try:

            hash_object = hashlib.new(
                cls.HASH_ALGORITHM
            )

            hash_object.update(
                data
            )

            return (
                hash_object.hexdigest()
            )

        except Exception:

            logger.exception(
                "Failed to hash bytes"
            )

            raise

    @classmethod
    def hash_file(
        cls,
        file_path: str
    ) -> str:

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

            hash_object = hashlib.new(
                cls.HASH_ALGORITHM
            )

            with open(
                path,
                "rb"
            ) as file:

                while True:

                    data = file.read(
                        cls.BUFFER_SIZE
                    )

                    if not data:

                        break

                    hash_object.update(
                        data
                    )

            file_hash = (
                hash_object.hexdigest()
            )

            logger.info(
                f"Generated file hash "
                f"for {path.name}"
            )

            return file_hash

        except PermissionError:

            logger.exception(
                "Permission denied"
            )

            raise

        except OSError:

            logger.exception(
                "OS error while "
                "hashing file"
            )

            raise

        except Exception:

            logger.exception(
                "Unexpected hashing error"
            )

            raise