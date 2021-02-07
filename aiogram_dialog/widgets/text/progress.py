from typing import Dict

from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.when import WhenCondition
from .base import Text


class Progress(Text):
    def __init__(self, field: str, width: int = 10, filled="🟥", empty="⬜", when: WhenCondition = None):
        super().__init__(when)
        self.field = field
        self.width = width
        self.filled = filled
        self.empty = empty

    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        percent = data.get(self.field)
        done = round((self.width * percent) / 100)
        rest = self.width - done

        return self.filled * done + self.empty * rest + f" {percent: 2.0f}%"
