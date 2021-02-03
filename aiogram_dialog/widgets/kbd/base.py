from typing import List, Optional

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.action import Actionable
from aiogram_dialog.widgets.when import WhenCondition


class Keyboard(Actionable):
    def __init__(self, id: Optional[str] = None, when: WhenCondition = None):
        super(Keyboard, self).__init__(id, when)

    async def render_kbd(self, data, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        if not self.is_(data, manager):
            return []
        return await self._render_kbd(data, manager)

    async def _render_kbd(self, data, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        raise NotImplementedError

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager) -> bool:
        return False
