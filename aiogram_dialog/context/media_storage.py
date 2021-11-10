from typing import Optional, Any

from aiogram.types import ContentType


class Media:
    def __init__(self, type: ContentType, url: Optional[str] = None,
                 path: Optional[str] = None, **kwargs):
        self.type = type
        self.url = url
        self.path = path
        self.kwargs = kwargs


class MediaIdStorage:
    def __init__(self):
        self.cache = {}

    async def get_media_id(self, path: str,
                           type: ContentType) -> Optional[int]:
        return self.cache.get((path, type))

    async def get_media_source(self, media: Media) -> Any:  # TODO hint
        if media.path:
            mid = await self.get_media_id(media.path, media.type)
            if mid is not None:
                return mid
            else:
                return open(media.path, "rb")
        return media.url

    async def save_media_id(self, media: Media, media_id: str) -> None:
        if media.path:
            self.cache[(media.path, media.type)] = media_id
