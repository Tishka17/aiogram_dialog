from typing import Callable, Union, Dict

from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.when import Whenable, WhenCondition


class Text(Whenable):
    def __init__(self, when: WhenCondition = None):
        super().__init__(when)

    async def render_text(self, data: Dict, manager: DialogManager) -> str:
        if not self.is_(data, manager):
            return ""
        return await self._render_text(data, manager)

    async def _render_text(self, data, manager: DialogManager) -> str:
        raise NotImplementedError


class Const(Text):
    def __init__(self, text: str, when: WhenCondition = None):
        super().__init__(when)
        self.text = text

    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        return self.text
