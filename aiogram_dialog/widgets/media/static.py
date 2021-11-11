from typing import Optional, Any, Dict

from aiogram.types import ContentType

from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.utils import MediaAttachment
from aiogram_dialog.widgets.when import Whenable, WhenCondition


class StaticMedia(Whenable):
    def __init__(
            self,
            type: ContentType,
            path: Optional[str],
            url: Optional[str],
            media_params: Dict = None,
            when: WhenCondition = None
    ):
        super().__init__(when)
        self.type = type
        self.path = path
        self.url = url
        self.media_params = media_params

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
