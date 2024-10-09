from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from aiogram.types import ContentType


@dataclass
class MediaId:
    file_id: str
    file_unique_id: Optional[str] = None

    def __eq__(self, other):
        if type(other) is not MediaId:
            return False
        if self.file_unique_id is None or other.file_unique_id is None:
            return self.file_id == other.file_id
        return self.file_unique_id == other.file_unique_id


class MediaAttachment:
    def __init__(
            self,
            type: ContentType,
            url: Optional[str] = None,
            path: Union[str, Path, None] = None,
            file_id: Optional[MediaId] = None,
            file_bytes: bytes = None,
            filename: str = None,
            use_pipe: bool = False,
            **kwargs,
    ):
        if not (url or path or file_id or file_bytes):
            raise ValueError("Neither url nor path nor file_id not file_bytes are provided")
        if file_bytes and not filename:
            raise ValueError("file_bytes must be given with filename")
        self.type = type
        self.url = url
        self.path = path
        self.file_id = file_id
        self.use_pipe = use_pipe
        self.kwargs = kwargs
        self.file_bytes = file_bytes
        self.filename = filename

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return (
            self.type == other.type and
            self.url == other.url and
            self.path == other.path and
            self.file_id == other.file_id and
            self.use_pipe == other.use_pipe and
            self.kwargs == other.kwargs and
            self.file_bytes == other.file_bytes and
            self.filename == other.filename
        )
