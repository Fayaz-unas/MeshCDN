import logging

from models.file_metadata import (
    FileMetadata
)

from models.chunk_metadata import (
    ChunkMetadata
)

logger = logging.getLogger(
    __name__
)


class SharedFileService:

    def __init__(self):

        self._shared_files = {}

    def register_file(
        self,
        file_hash: str,
        file_metadata: FileMetadata,
        chunks: list[ChunkMetadata]
    ) -> None:

        if file_hash in self._shared_files:

            logger.warning(
                f"File already shared: "
                f"{file_hash}"
            )

            return

        self._shared_files[
            file_hash
        ] = {

            "file_metadata":
                file_metadata,

            "chunks":
                chunks

        }

        logger.info(
            f"Registered shared file: "
            f"{file_metadata.file_name}"
        )

    def unregister_file(
        self,
        file_hash: str
    ) -> None:

        if (
            file_hash
            in
            self._shared_files
        ):

            del self._shared_files[
                file_hash
            ]

            logger.info(
                f"Removed shared file: "
                f"{file_hash}"
            )

    def get_shared_file(
        self
        ,file_hash: str
    ) -> dict | None:
        
        return self._shared_files.get(
            file_hash
        )

    def get_file_metadata(
        self,
        file_hash: str
    ) -> FileMetadata | None:
        
        shared_file = (
            self.get_shared_file(
                file_hash
            )
        )
        
        
        if shared_file is None:
            return None
        
        
        return shared_file[
            "file_metadata"
       ]
    


    def get_chunk(        
        self,
        file_hash: str,
        chunk_index: int
    ) -> ChunkMetadata | None:
        
        shared_file = (
            self.get_shared_file(
                file_hash
            )
        )
        
        
        if shared_file is None:
            return None

        chunks = shared_file[
            "chunks"
        ]
        
        if (
            chunk_index < 0
            or
            chunk_index >= len(chunks)
        ):
            return None

        return chunks[
            chunk_index
        ]
    
    
    def has_file(
        self,
        file_hash: str
    ) -> bool:

        return (
            file_hash
            in
            self._shared_files
        )

    def get_all_files(
        self
    ) -> dict:

        return (
            self._shared_files
        )
