from pathlib import Path
from typing import Any, Optional, Union

from aiogram.types import ContentType
from cachetools import LRUCache

from aiogram_dialog.api.entities import MediaId
from aiogram_dialog.api.protocols import MediaIdStorageProtocol


class MediaIdStorage(MediaIdStorageProtocol):
    cache: LRUCache[Any, Any]

    def __init__(self, maxsize: int = 10240) -> None:
        self.cache = LRUCache(maxsize=maxsize)

    async def get_media_id(
        self,
        path: Optional[Union[str, Path]],
        url: Optional[str],
        type: ContentType,
    ) -> Optional[MediaId]:
        if not path and not url:
            return None
        return self.cache.get((path, url, type))

    async def save_media_id(
        self,
        path: Optional[Union[str, Path]],
        url: Optional[str],
        type: ContentType,
        media_id: MediaId,
    ) -> None:
        if not path and not url:
            return None
        self.cache[(path, url, type)] = media_id
