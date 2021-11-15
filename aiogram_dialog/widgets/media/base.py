from typing import Optional, Any

from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.utils import MediaAttachment
from aiogram_dialog.widgets.when import Whenable


class Media(Whenable):
    async def render_media(
            self,
            data: Any,
            manager: DialogManager
    ) -> Optional[MediaAttachment]:
        if not self.is_(data, manager):
            return None
        return await self._render_media(data, manager)

    async def _render_media(
            self,
            data: Any,
            manager: DialogManager
    ) -> Optional[MediaAttachment]:
        return None
