from abc import abstractmethod
from pathlib import Path
from typing import Optional, Protocol, Union

from aiogram.types import ContentType

from aiogram_dialog.api.entities import MediaId


class MediaIdStorageProtocol(Protocol):
    @abstractmethod
    async def get_media_id(
        self,
        path: Optional[Union[str, Path]],
        url: Optional[str],
        type: ContentType,
    ) -> Optional[MediaId]:
        raise NotImplementedError

    @abstractmethod
    async def save_media_id(
        self,
        path: Optional[Union[str, Path]],
        url: Optional[str],
        type: ContentType,
        media_id: MediaId,
    ) -> None:
        raise NotImplementedError
