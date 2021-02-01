from typing import List, Callable, Union

from aiogram.types import InlineKeyboardButton, CallbackQuery

from dialog.dialog import Dialog
from dialog.manager.manager import DialogManager
from dialog.widgets.when import Whenable


class Keyboard(Whenable):
    def __init__(self, when: Union[str, Callable] = None):
        super(Keyboard, self).__init__(when)

    async def render_kbd(self, data) -> List[List[InlineKeyboardButton]]:
        if not self.is_(data):
            return []
        return await self._render_kbd(data)

    async def _render_kbd(self, data) -> List[List[InlineKeyboardButton]]:
        raise NotImplementedError

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager) -> bool:
        return False
