from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition

from .base import Text


class Progress(Text):
    def __init__(
            self,
            field: str,
            width: int = 10,
            total: int = 100,
            filled="🟥",
            empty="⬜",
            when: WhenCondition = None,
    ):
        super().__init__(when)
        self.field = field
        self.width = width
        self.total = total
        self.filled = filled
        self.empty = empty

    async def _render_text(
            self, data: dict, manager: DialogManager,
    ) -> str:
        if manager.is_preview():
            value = 15
        else:
            value = data.get(self.field)

        done = round((self.width * value) / self.total)
        rest = self.width - done
        percent = (value / self.total) * 100

        return self.filled * done + self.empty * rest + f" {percent: 2.0f}%"
