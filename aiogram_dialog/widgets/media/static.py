from typing import Optional, Any, Dict

from aiogram.types import ContentType

from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.utils import MediaAttachment
from .base import Media
from ..when import WhenCondition


class StaticMedia(Media):
    def __init__(
            self,
            *,
            path: Optional[str] = None,
            url: Optional[str] = None,
            type: ContentType = ContentType.PHOTO,
            media_params: Dict = None,
            when: WhenCondition = None,
    ):
        super().__init__(when)
        if not (url or path):
            raise ValueError("Neither url nor path are provided")
        self.type = type
        self.path = path
        self.url = url
        self.media_params = media_params or {}

    async def _render_media(
            self,
            data: Any,
            manager: DialogManager
    ) -> Optional[MediaAttachment]:
        return MediaAttachment(
            type=self.type,
            url=self.url,
            path=self.path,
            **self.media_params,
        )
