import logging

from services.download_service import (
    DownloadService,
)

logger = logging.getLogger(__name__)


class DownloadAPI:
    """
    Public API for downloading files.

    This class provides a stable entry point for the UI,
    CLI and future REST endpoints.

    It intentionally contains no download logic and
    delegates all work to DownloadService.
    """

    @staticmethod
    def download(
        file_hash: str,
    ) -> dict:

        logger.info(
            "Download requested for file: %s",
            file_hash,
        )

        result = (
            DownloadService().download(
                file_hash
            )
        )

        logger.info(
            "Download completed for file: %s",
            file_hash,
        )

        return result