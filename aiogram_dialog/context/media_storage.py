from typing import Optional, Any

from aiogram.types import ContentType


class MediaIdStorage:
    def __init__(self):
        self.cache = {}

    async def get_media_id(self, path: str,
                           type: ContentType) -> Optional[int]:
        return self.cache.get((path, type))

    async def save_media_id(self, path: str,
                            type: ContentType,
                            media_id: str) -> None:
        self.cache[(path, type)] = media_id
