from typing import Optional, Any, Dict, Union

from aiogram.types import ContentType

from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.manager.protocols import MediaAttachment
from aiogram_dialog.widgets.text import Text, Const
from .base import Media
from ..when import WhenCondition


class StaticMedia(Media):
    def __init__(
            self,
            *,
            path: Union[Text, str, None] = None,
            url: Union[Text, str, None] = None,
            type: ContentType = ContentType.PHOTO,
            media_params: Dict = None,
            when: WhenCondition = None,
    ):
        super().__init__(when)
        if not (url or path):
            raise ValueError("Neither url nor path are provided")
        self.type = type
        if isinstance(path, str):
            path = Const(path)
        self.path = path
        if isinstance(url, str):
            url = Const(url)
        self.url = url
        self.media_params = media_params or {}

    async def _render_media(
            self,
            data: Any,
            manager: DialogManager
    ) -> Optional[MediaAttachment]:
        if self.url:
            url = await self.url.render_text(data, manager)
        else:
            url = None
        if self.path:
            path = await self.path.render_text(data, manager)
        else:
            path = None

        return MediaAttachment(
            type=self.type,
            url=url,
            path=path,
            **self.media_params,
        )
