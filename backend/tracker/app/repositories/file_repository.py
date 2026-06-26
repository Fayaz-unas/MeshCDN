from typing import Optional

from sqlalchemy.orm import Session

from app.models.file import File


class FileRepository:

    @staticmethod
    def create_file(
        db: Session,
        file: File
    ):
        db.add(file)
        db.commit()
        db.refresh(file)

        return file

    @staticmethod
    def get_by_id(
        db: Session,
        file_id: int
    ) -> Optional[File]:
        return (
            db.query(File)
            .filter(File.id == file_id)
            .first()
        )

    @staticmethod
    def get_by_hash(
        db: Session,
        file_hash: str
    ) -> Optional[File]:
        return (
            db.query(File)
            .filter(File.file_hash == file_hash)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session
    ):
        return (
            db.query(File)
            .filter(File.is_active == True)
            .all()
        )

    @staticmethod
    def exists_by_hash(
        db: Session,
        file_hash: str
    ) -> bool:
        return (
            db.query(File)
            .filter(File.file_hash == file_hash)
            .first()
            is not None
        )

    @staticmethod
    def update_file(
        db: Session,
        file: File
    ):
        db.commit()
        db.refresh(file)

        return file

    @staticmethod
    def delete_file(
        db: Session,
        file: File
    ):
        file.is_active = False

        db.commit()
        db.refresh(file)

        return file