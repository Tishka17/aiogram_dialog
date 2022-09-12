from typing import Any, Optional

from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.api.internal import DialogManager
from aiogram_dialog.widgets.when import Whenable


class Media(Whenable):
    async def render_media(
            self, data: Any, manager: DialogManager,
    ) -> Optional[MediaAttachment]:
        if not self.is_(data, manager):
            return None
        return await self._render_media(data, DialogManager)

    async def _render_media(
            self, data: Any, manager: DialogManager,
    ) -> Optional[MediaAttachment]:
        return None
