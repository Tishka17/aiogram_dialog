from typing import List

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.when import Whenable, WhenCondition


class Keyboard(Whenable):
    def __init__(self, when: WhenCondition = None):
        super(Keyboard, self).__init__(when)

    async def render_kbd(self, data, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        if not self.is_(data, manager):
            return []
        return await self._render_kbd(data, manager)

    async def _render_kbd(self, data, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        raise NotImplementedError

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager) -> bool:
        return False
