import logging
from threading import Lock

from models.chunk_metadata import ChunkMetadata
from models.file_metadata import FileMetadata
from models.manifest import Manifest

logger = logging.getLogger(__name__)


class SharedFileService:
    """
    Local shared file registry.

    Maintains all files currently shared by this peer.

    Singleton:
        There is exactly one registry for the lifetime
        of the peer process.
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):

        if cls._instance is None:

            with cls._lock:

                if cls._instance is None:

                    cls._instance = super().__new__(cls)

                    cls._instance._shared_files = {}

        return cls._instance

    # ---------------------------------------------------------
    # Register
    # ---------------------------------------------------------

    def register_file(
        self,
        *,
        file_hash: str,
        manifest: Manifest,
        file_metadata: FileMetadata,
        chunks: list[ChunkMetadata],
    ) -> None:

        if file_hash in self._shared_files:

            logger.warning(
                "File already shared: %s",
                file_hash,
            )

            return

        self._shared_files[file_hash] = {

            "file_hash": file_hash,

            "manifest_hash":
                manifest.manifest_hash,

            "manifest":
                manifest,

            "file_metadata":
                file_metadata,

            "chunks":
                chunks,
        }

        logger.info(
            "Registered shared file: %s",
            manifest.file_name,
       )

    # ---------------------------------------------------------
    # Register Downloaded File
    # ---------------------------------------------------------

    def register_downloaded_file(
        self,
        *,
        file_hash: str,
        manifest: Manifest,
        file_metadata: FileMetadata | None = None,
        chunks: list[ChunkMetadata] | None = None,
    ) -> None:
        
        self.register_file(
        file_hash=file_hash,
        manifest=manifest,
        file_metadata=file_metadata,
        chunks=chunks,
    )
        
        logger.info(
        "Registered downloaded file: %s",
        manifest.file_name,
        )
    # ---------------------------------------------------------
    # Unregister
    # ---------------------------------------------------------

    def unregister_file(
        self,
        file_hash: str,
    ) -> None:

        if file_hash not in self._shared_files:
            return

        del self._shared_files[file_hash]

        logger.info(
            "Removed shared file: %s",
            file_hash,
        )

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    def has_file(
        self,
        file_hash: str,
    ) -> bool:

        return file_hash in self._shared_files

    def get_shared_file(
        self,
        file_hash: str,
    ) -> dict | None:

        return self._shared_files.get(
            file_hash
        )

    def get_file_metadata(
        self,
        file_hash: str,
    ) -> FileMetadata | None:

        shared_file = self.get_shared_file(
            file_hash
        )

        if shared_file is None:
            return None

        return shared_file[
            "file_metadata"
        ]

    def get_manifest(
        self,
        file_hash: str,
    ) -> Manifest | None:

        shared_file = self.get_shared_file(
            file_hash
        )

        if shared_file is None:
            return None

        return shared_file[
            "manifest"
        ]

    def get_chunks(
        self,
        file_hash: str,
    ) -> list[ChunkMetadata] | None:

        shared_file = self.get_shared_file(
            file_hash
        )

        if shared_file is None:
            return None

        return shared_file[
            "chunks"
        ]

    def get_chunk(
        self,
        file_hash: str,
        chunk_index: int,
    ) -> ChunkMetadata | None:

        chunks = self.get_chunks(
            file_hash
        )

        if chunks is None:
            return None

        if (
            chunk_index < 0
            or
            chunk_index >= len(chunks)
        ):
            return None

        return chunks[
            chunk_index
        ]

    def get_all_files(
        self,
    ) -> dict:
        """
        Get a copy of all shared files.

        Returns a copy to prevent external modification
        of the internal registry.
        """

        return dict(
            self._shared_files
        )

    def total_shared_files(
        self,
    ) -> int:

        return len(
            self._shared_files
        )

    def clear(
        self,
    ) -> None:

        self._shared_files.clear()

        logger.info(
            "Shared file registry cleared."
        )