from dataclasses import dataclass


@dataclass
class FileMetadata:

    file_name: str

    file_path: str

    file_extension: str

    file_size_bytes: int