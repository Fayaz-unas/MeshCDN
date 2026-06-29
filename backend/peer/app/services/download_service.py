from __future__ import annotations

import logging
from pathlib import Path

from api.discovery_api import DiscoveryAPI
from api.peer_file_state_api import PeerFileStateAPI

from models.manifest import Manifest

from services.chunk_storage_service import (
    ChunkStorageService,
)

from services.file_reconstruction_service import (
    FileReconstructionService,
)

from services.manifest_service import (
    ManifestService,
)

from services.peer_download_service import (
    PeerDownloadService,
)

from services.peer_identity_service import (
    PeerIdentityService,
)

from services.shared_file_service import (
    SharedFileService,
)

logger = logging.getLogger(__name__)


class DownloadService:
    """
    Coordinates the complete download workflow.

    Responsibilities
    ----------------
    1. Discover swarm
    2. Validate swarm
    3. Select download peer
    4. Download every chunk
    5. Reconstruct file
    6. Verify integrity
    7. Register locally
    8. Publish ownership
    """

    def __init__(self):

        self.shared_file_service = (
            SharedFileService()
        )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def download(
        self,
        file_hash: str,
    ) -> dict:

        logger.info(
            "Starting download: %s",
            file_hash,
        )

        manifest = None

        try:

            swarm = self._discover_swarm(
                file_hash
            )

            manifest = ManifestService.from_swarm(
                swarm
            )

            peer = self._select_peer(
                swarm
            )

            self._download_chunks(
                manifest,
                peer,
            )

            output = self._reconstruct_file(
                manifest
            )

            self._verify_download(
                manifest,
                output,
            )

            self._register_download(
                manifest
            )

            self._publish_ownership(
                manifest
            )

            logger.info(
                "Download completed."
            )

            return {

                "status":
                "success",

                "file_hash":
                manifest.file_hash,

                "file_name":
                manifest.file_name,

                "output_path":
                str(output),

            }

        except Exception:

            logger.exception(
                "Download failed."
            )

            if manifest:
                self._rollback(
                    manifest.file_hash
                )

            raise

    # ---------------------------------------------------------
    # Discovery
    # ---------------------------------------------------------

    def _discover_swarm(
        self,
        file_hash: str,
    ) -> dict:

        logger.info(
            "Discovering swarm for %s",
            file_hash,
        )

        swarm = DiscoveryAPI.discover_swarm(
            file_hash
        )

        if swarm is None:

            raise RuntimeError(
                "Tracker returned no swarm."
            )

        if not swarm.get(
            "swarm",
            {},
        ).get(
            "file_available",
            False,
        ):

            raise RuntimeError(
                "File is currently unavailable."
            )

        peers = swarm.get(
            "peers",
            []
        )

        if not peers:

            raise RuntimeError(
                "No online peers available."
            )

        logger.info(

            "Found %s online peer(s).",

            len(peers)

        )

        return swarm

    # ---------------------------------------------------------
    # Manifest Construction
    # ---------------------------------------------------------

    def _select_peer(
        self,
        swarm: dict,
    ) -> dict:

        peers = swarm["peers"]

        if not peers:

            raise RuntimeError(
                "No peers available."
            )

        #
        # Future:
        #
        # Multi-peer scheduling
        # Rarest First
        # Latency selection
        #
        # v1:
        #
        # Choose peer owning
        # the highest number of chunks.
        #

        peer = max(

            peers,

            key=lambda p:
            p["owned_chunk_count"]

        )

        logger.info(

            "Selected peer %s (%s:%s)",

            peer["peer_id"],

            peer["ip_address"],

            peer["port"]

        )

        return peer
    
    
    # ---------------------------------------------------------
    # Download
    # ---------------------------------------------------------

    def _download_chunks(
        self,
        manifest: Manifest,
        peer: dict,
    ) -> None:

        logger.info(
            "Downloading %s chunks.",
            manifest.total_chunks,
        )

        downloader = (
            PeerDownloadService()
        )

        for chunk_index in range(
            manifest.total_chunks
        ):

            #
            # Resume support
            #

            if ChunkStorageService.chunk_exists(

                manifest.file_hash,

                chunk_index,

            ):

                logger.debug(

                    "Chunk %s already exists.",

                    chunk_index,

                )

                continue

            logger.info(

                "Downloading chunk %s/%s",

                chunk_index + 1,

                manifest.total_chunks,

            )

            success = (
                downloader.download_chunk(

                    peer_host=
                    peer["ip_address"],

                    peer_port=
                    peer["port"],

                    file_hash=
                    manifest.file_hash,

                    chunk_index=
                    chunk_index,

                )
            )

            if not success:

                raise RuntimeError(

                    f"Failed to download "

                    f"chunk {chunk_index}"

                )

        if (

            not

            ChunkStorageService.has_all_chunks(

                manifest.file_hash,

                manifest.total_chunks,

            )

        ):

            raise RuntimeError(

                "Download incomplete."

            )

        logger.info(
            "All chunks downloaded."
        )

    # ---------------------------------------------------------
    # Reconstruction
    # ---------------------------------------------------------

    def _reconstruct_file(
        self,
        manifest: Manifest,
    ) -> Path:

        logger.info(
            "Reconstructing file."
        )

        reconstructed = (

            FileReconstructionService

            .reconstruct_to_downloads(

                file_hash=
                manifest.file_hash,

                total_chunks=
                manifest.total_chunks,

                file_name=
                manifest.file_name,

            )

        )

        logger.info(

            "Reconstruction completed: %s",

            reconstructed,

        )

        return reconstructed
    
    # ---------------------------------------------------------
    # Verification
    # ---------------------------------------------------------

    def _verify_download(
        self,
        manifest: Manifest,
        output: Path,
    ) -> None:

        logger.info(
            "Verifying reconstructed file."
        )

        verified = (
            FileReconstructionService
            .verify_integrity(
                output,
                manifest.file_hash,
            )
        )

        if not verified:

            raise RuntimeError(
                "Downloaded file failed integrity verification."
            )

        logger.info(
            "Integrity verification passed."
        )

    # ---------------------------------------------------------
    # Local Registration
    # ---------------------------------------------------------

    def _register_download(
        self,
        manifest: Manifest,
    ) -> None:

        logger.info(
            "Registering downloaded file locally."
        )

        self.shared_file_service.register_downloaded_file(
            file_hash=manifest.file_hash,
            manifest=manifest,
        )

        logger.info(
            "Local registration completed."
        )

    # ---------------------------------------------------------
    # Publish Ownership
    # ---------------------------------------------------------

    def _publish_ownership(
        self,
        manifest: Manifest,
    ) -> None:

        logger.info(
            "Publishing ownership to tracker."
        )

        peer_id = (
            PeerIdentityService.get_peer_id()
        )

        chunk_map = [
            [
                0,
                manifest.total_chunks - 1,
            ]
        ]

        PeerFileStateAPI.register_peer_file_state(

            peer_id=peer_id,

            file_hash=manifest.file_hash,

            chunk_map=chunk_map,

            owned_chunk_count=manifest.total_chunks,

        )

        logger.info(
            "Tracker updated successfully."
        )

    # ---------------------------------------------------------
    # Rollback
    # ---------------------------------------------------------

    def _rollback(
        self,
        file_hash: str,
    ) -> None:

        logger.warning(
            "Rolling back failed download."
        )

        try:

            ChunkStorageService.delete_partial_download(
                file_hash
            )

        except Exception:

            logger.exception(
                "Failed to delete partial download."
            )

        try:

            self.shared_file_service.unregister_file(
                file_hash
            )

        except Exception:

            logger.exception(
                "Failed to unregister local file."
            )

        logger.info(
            "Rollback completed."
        )