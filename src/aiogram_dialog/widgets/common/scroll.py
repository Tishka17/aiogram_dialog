from typing import Dict, Protocol

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.protocols import DialogManager


class Scroll(Protocol):
    async def get_page_count(self, data: Dict, manager: DialogManager) -> int:
        raise NotImplementedError

    async def get_page(self, manager: DialogManager) -> int:
        raise NotImplementedError

    async def set_page(
            self, event: ChatEvent, page: int, manager: DialogManager,
    ) -> None:
        raise NotImplementedError
