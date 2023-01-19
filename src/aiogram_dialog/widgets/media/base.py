from typing import Any, Optional

from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.api.internal import MediaWidget
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import BaseWidget, Whenable, WhenCondition


class Media(BaseWidget, Whenable, MediaWidget):
    def __init__(self, when: WhenCondition = None):
        super().__init__(when=when)

    async def render_media(
            self, data: Any, manager: DialogManager,
    ) -> Optional[MediaAttachment]:
        if not self.is_(data, manager):
            return None
        return await self._render_media(data, manager)

    async def _render_media(
            self, data: Any, manager: DialogManager,
    ) -> Optional[MediaAttachment]:
        return None
