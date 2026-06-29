import logging

from models.chunk_metadata import ChunkMetadata
from models.manifest import Manifest

from api.file_api import FileAPI
from api.peer_file_state_api import PeerFileStateAPI

from services.file_service import FileService
from services.hash_service import HashService
from services.chunk_service import ChunkService
from services.chunk_reader_service import ChunkReaderService
from services.chunk_storage_service import ChunkStorageService
from services.manifest_service import ManifestService
from services.shared_file_service import SharedFileService
from services.peer_identity_service import PeerIdentityService


logger = logging.getLogger(__name__)


class ShareService:
    """
    Coordinates the complete MeshCDN sharing workflow.

    Responsibilities
    ----------------
    - Validate local file
    - Generate hashes
    - Create chunk metadata
    - Store chunks
    - Generate manifest
    - Register locally
    - Publish metadata to tracker

    This service intentionally contains no hashing,
    chunking or networking logic. It orchestrates
    existing services.
    """

    def __init__(self):

        self.shared_files = SharedFileService()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def share(
        self,
        file_path: str,
    ) -> dict:

        logger.info(
            "Sharing file: %s",
            file_path,
        )

        file_hash = None

        try:

            file_metadata = FileService.register_file(
                file_path
            )

            file_hash = HashService.hash_file(
                file_metadata.file_path
            )

            if self.shared_files.has_file(
                file_hash
            ):
                raise ValueError(
                    "File is already shared."
                )

            chunks = ChunkService.create_chunks(
                file_metadata
            )

            self._store_chunks(
                file_metadata.file_path,
                file_hash,
                chunks,
            )

            manifest = (
                ManifestService.create_manifest(

                    file_hash=file_hash,

                    file_name=file_metadata.file_name,

                    file_size_bytes=file_metadata.file_size_bytes,

                    chunk_size_bytes=ChunkService.CHUNK_SIZE_BYTES,

                    chunks=chunks,
                )
            )

            manifest_path = (
                ManifestService.save_manifest(
                    manifest
                )
            )

            self.shared_files.register_file(

                file_hash=file_hash,

                manifest=manifest,

                file_metadata=file_metadata,

                chunks=chunks,
            )

            chunk_map = [
                [
                    0,
                    len(chunks) - 1,
                ]
            ]

            self._publish_to_tracker(
                manifest,
                chunk_map,
            )

            logger.info(
                "Successfully shared '%s'",
                file_metadata.file_name,
            )

            return {

                "file_hash":
                    manifest.file_hash,

                "manifest_hash":
                    manifest.manifest_hash,

                "manifest_path":
                    str(manifest_path),

                "file_name":
                    file_metadata.file_name,

                "total_chunks":
                    len(chunks),

                "chunk_map":
                    chunk_map,
            }

        except Exception:

            logger.exception(
                "Share workflow failed."
            )

            if file_hash:
                self._rollback(
                    file_hash
                )

            raise

    # ---------------------------------------------------------
    # Private Helpers
    # ---------------------------------------------------------

    def _store_chunks(
        self,
        file_path: str,
        file_hash: str,
        chunks: list[ChunkMetadata],
    ) -> None:
        """
        Read every generated chunk from the original file
        and persist it to local storage.
        """

        logger.info(
            "Storing %s chunks.",
            len(chunks),
        )

        for chunk in chunks:

            data = ChunkReaderService.read_chunk(
                file_path=file_path,
                chunk=chunk,
            )

            ChunkStorageService.save_chunk(
                file_hash=file_hash,
                chunk_index=chunk.chunk_index,
                data=data,
            )

        logger.info(
            "Stored all chunks successfully."
        )

    # ---------------------------------------------------------

    def _publish_to_tracker(
        self,
        manifest: Manifest,
        chunk_map: list[list[int]],
    ) -> None:
        """
        Publish file metadata and ownership
        information to the tracker.
        """

        peer_id = (
            PeerIdentityService.get_peer_id()
        )

        logger.info(
            "Publishing '%s' to tracker.",
            manifest.file_name,
        )

        FileAPI.register_file(

            file_hash=manifest.file_hash,

            manifest_hash=manifest.manifest_hash,

            file_name=manifest.file_name,

            file_size=manifest.file_size_bytes,

            chunk_size=manifest.chunk_size_bytes,

            total_chunks=manifest.total_chunks,

            mime_type=manifest.mime_type,

            peer_id=peer_id,
        )

        PeerFileStateAPI.register_peer_file_state(

            peer_id=peer_id,

            file_hash=manifest.file_hash,

            chunk_map=chunk_map,

            owned_chunk_count=manifest.total_chunks,
        )

        logger.info(
            "Tracker registration completed."
        )

    # ---------------------------------------------------------

    def _rollback(
        self,
        file_hash: str,
    ) -> None:
        """
        Roll back any partially completed
        share operation.
        """

        logger.warning(
            "Rolling back share operation."
        )

        try:

            self.shared_files.unregister_file(
                file_hash
            )

        except Exception:

            logger.exception(
                "Failed to remove shared file."
            )

        try:

            ChunkStorageService.delete_partial_download(
                file_hash
            )

        except Exception:

            logger.exception(
                "Failed to clean storage."
            )