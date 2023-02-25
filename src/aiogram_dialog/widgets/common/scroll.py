from typing import Dict, Protocol

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import ManagedWidget


class Scroll(Widget, Protocol):
    async def get_page_count(self, data: Dict, manager: DialogManager) -> int:
        raise NotImplementedError

    async def get_page(self, manager: DialogManager) -> int:
        raise NotImplementedError

    async def set_page(
            self, event: ChatEvent, page: int, manager: DialogManager,
    ) -> None:
        raise NotImplementedError

    def managed(self, manager: DialogManager) -> "ManagedScroll":
        raise NotImplementedError


class ManagedScroll(ManagedWidget[Scroll]):
    async def get_page_count(self, data: Dict) -> int:
        return await self.widget.get_page_count(data, self.manager)

    async def get_page(self) -> int:
        return await self.widget.get_page(self.manager)

    async def set_page(self, page: int) -> None:
        return await self.widget.set_page(
            self.manager.event, page, self.manager,
        )
