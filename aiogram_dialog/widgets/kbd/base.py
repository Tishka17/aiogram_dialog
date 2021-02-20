from typing import List, Optional

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.action import Actionable
from aiogram_dialog.widgets.when import WhenCondition, Whenable


class Keyboard(Actionable, Whenable):
    def __init__(self, id: Optional[str] = None, when: WhenCondition = None):
        Actionable.__init__(self, id)
        Whenable.__init__(self, when)

    async def render_keyboard(self, data, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        if not self.is_(data, manager):
            return []
        return await self._render_keyboard(data, manager)

    async def _render_keyboard(self, data, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        raise NotImplementedError

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager) -> bool:
        return False
