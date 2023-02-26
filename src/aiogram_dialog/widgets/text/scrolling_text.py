from typing import Dict, Optional

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import (
    Actionable, ManagedScroll, Scroll, WhenCondition,
)
from aiogram_dialog.widgets.text import Text


class ScrollingText(Text, Actionable, Scroll):
    def __init__(
            self,
            text: Text,
            id: str,
            page_size: int = 0,
            when: WhenCondition = None,
    ):
        Text.__init__(self, when=when)
        Actionable.__init__(self, id=id)
        self.text = text
        self.page_size = page_size

    def _get_page_count(
            self,
            text: str,
    ) -> int:
        return len(text) // self.page_size + bool(len(text) % self.page_size)

    async def _render_contents(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> str:
        return await self.text.render_text(data, manager)

    async def _render_text(self, data, manager: DialogManager) -> str:
        text = await self._render_contents(data, manager)
        pages = self._get_page_count(text)
        page = await self.get_page(manager)
        last_page = pages - 1
        current_page = min(last_page, page)
        page_offset = current_page * self.page_size

        return text[page_offset: page_offset + self.page_size]

    async def get_page_count(self, data: Dict, manager: DialogManager) -> int:
        text = await self._render_contents(data, manager)
        return self._get_page_count(text)

    async def get_page(self, manager: DialogManager) -> int:
        return self.get_widget_data(manager, 0)

    async def set_page(
            self, event: ChatEvent, page: int, manager: DialogManager,
    ) -> None:
        self.set_widget_data(manager, page)

    def managed(self, manager: DialogManager):
        return ManagedScroll(self, manager)

    def find(self, widget_id: str) -> Optional[Widget]:
        if self.widget_id == widget_id:
            return self
        return None
