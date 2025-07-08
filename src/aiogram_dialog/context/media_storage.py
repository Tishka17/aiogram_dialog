import os
from typing import NamedTuple, Optional, cast

from aiogram.types import ContentType
from cachetools import LRUCache

from aiogram_dialog.api.entities import MediaId
from aiogram_dialog.api.protocols import MediaIdStorageProtocol


class CachedMediaId(NamedTuple):
    media_id: MediaId
    mtime: Optional[float]


class MediaIdStorage(MediaIdStorageProtocol):
    def __init__(self, maxsize=10240):
        self.cache = LRUCache(maxsize=maxsize)

    async def get_media_id(
            self,
            path: Optional[str],
            url: Optional[str],
            type: ContentType,
    ) -> Optional[MediaId]:
        if not path and not url:
            return None
        cached = cast(
            Optional[CachedMediaId],
            self.cache.get((path, url, type)),
        )
        if cached is None:
            return None

        if cached.mtime is not None:
            mtime = self._get_file_mtime(path)
            if mtime is not None and mtime != cached.mtime:
                return None
        return cached.media_id

    def _get_file_mtime(self, path: Optional[str]) -> Optional[float]:
        if not path:
            return None
        if not os.path.exists(path):  # noqa: PTH110
            return None
        return os.path.getmtime(path)  # noqa: PTH204

    async def save_media_id(
            self,
            path: Optional[str],
            url: Optional[str],
            type: ContentType,
            media_id: MediaId,
    ) -> None:
        if not path and not url:
            return
        self.cache[(path, url, type)] = CachedMediaId(
            media_id,
            self._get_file_mtime(path),
        )
