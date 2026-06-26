from typing import List

from sqlalchemy.orm import Session

from app.models.file import File
from app.repositories.file_repository import FileRepository
from app.repositories.peer_repository import PeerRepository
from app.schemas.file_schema import RegisterFileRequest


class FileService:

    @staticmethod
    def register_file(
        db: Session,
        request: RegisterFileRequest
    ) -> File:

        peer = PeerRepository.get_by_peer_id(
            db,
            request.peer_id
        )

        if peer is None:
            raise ValueError("Peer not found.")

        if FileRepository.exists_by_hash(
            db,
            request.file_hash
        ):
            raise ValueError("File already registered.")

        file = File(
            file_hash=request.file_hash,
            file_name=request.file_name,
            file_size=request.file_size,
            chunk_size=request.chunk_size,
            total_chunks=request.total_chunks,
            mime_type=request.mime_type,
            created_by_peer_id=peer.id
        )

        return FileRepository.create_file(
            db,
            file
        )

    @staticmethod
    def get_file_by_hash(
        db: Session,
        file_hash: str
    ):

        file = FileRepository.get_by_hash(
            db,
            file_hash
        )

        if file is None:
            raise ValueError("File not found.")

        return file

    @staticmethod
    def get_all_files(
        db: Session
    ) -> List[File]:

        return FileRepository.get_all(db)

    @staticmethod
    def delete_file(
        db: Session,
        file_hash: str
    ):

        file = FileRepository.get_by_hash(
            db,
            file_hash
        )

        if file is None:
            raise ValueError("File not found.")

        return FileRepository.delete_file(
            db,
            file
        )