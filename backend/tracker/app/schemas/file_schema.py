from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RegisterFileRequest(BaseModel):
    file_hash: str
    manifest_hash: str
    file_name: str
    file_size: int
    chunk_size: int
    total_chunks: int
    mime_type: Optional[str] = None
    peer_id: str


class FileMetadataResponse(BaseModel):
    id: int
    file_hash: str
    manifest_hash: str
    file_name: str
    file_size: int
    chunk_size: int
    total_chunks: int
    mime_type: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    id: int
    file_hash: str
    manifest_hash: str
    file_name: str
    file_size: int
    total_chunks: int
    mime_type: Optional[str]

    class Config:
        from_attributes = True