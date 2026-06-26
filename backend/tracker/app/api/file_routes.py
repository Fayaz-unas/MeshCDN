from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.file_schema import (
    RegisterFileRequest,
    FileMetadataResponse,
    FileListResponse,
)
from app.services.file_service import FileService

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


@router.post(
    "",
    response_model=FileMetadataResponse,
    status_code=status.HTTP_201_CREATED
)
def register_file(
    request: RegisterFileRequest,
    db: Session = Depends(get_db)
):
    try:
        return FileService.register_file(
            db,
            request
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.get(
    "",
    response_model=List[FileListResponse]
)
def get_all_files(
    db: Session = Depends(get_db)
):
    return FileService.get_all_files(db)


@router.get(
    "/{file_hash}",
    response_model=FileMetadataResponse
)
def get_file(
    file_hash: str,
    db: Session = Depends(get_db)
):
    try:
        return FileService.get_file_by_hash(
            db,
            file_hash
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.delete(
    "/{file_hash}",
    response_model=FileMetadataResponse
)
def delete_file(
    file_hash: str,
    db: Session = Depends(get_db)
):
    try:
        return FileService.delete_file(
            db,
            file_hash
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )