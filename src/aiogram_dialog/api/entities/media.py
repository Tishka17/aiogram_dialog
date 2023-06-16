from dataclasses import dataclass
from typing import Optional

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


@dataclass
class MediaBufferedData:
    file: bytes
    filename: str


class MediaAttachment:
    def __init__(
            self,
            type: ContentType,
            url: Optional[str] = None,
            path: Optional[str] = None,
            file_id: Optional[MediaId] = None,
            data: Optional[MediaBufferedData] = None,
            use_pipe: bool = False,
            **kwargs,
    ):
        if not (url or path or file_id or data):
            raise ValueError(
                "Neither url nor path not file_id not data are provided")
        self.type = type
        self.url = url
        self.path = path
        self.file_id = file_id
        self.data = data
        self.use_pipe = use_pipe
        self.kwargs = kwargs
