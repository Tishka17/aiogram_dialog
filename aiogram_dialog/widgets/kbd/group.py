from itertools import chain
from typing import List, Dict, Optional

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from .base import Keyboard
from ..when import WhenCondition


class Group(Keyboard):
    def __init__(self, *buttons: Keyboard, id: Optional[str] = None, keep_rows: bool = True, width: int = 0,
                 when: WhenCondition = None):
        super().__init__(id, when)
        self.buttons = buttons
        self.keep_rows = keep_rows
        self.width = width

    def find(self, widget_id):
        widget = super(Group, self).find(widget_id)
        if widget:
            return widget
        for btn in self.buttons:
            widget = btn.find(widget_id)
            if widget:
                return widget
        return None

    async def _render_keyboard(self, data: Dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        kbd: List[List[InlineKeyboardButton]] = []
        for b in self.buttons:
            b_kbd = await b.render_keyboard(data, manager)
            if self.keep_rows or not kbd:
                kbd += b_kbd
            else:
                kbd[0].extend(chain.from_iterable(b_kbd))
        if not self.keep_rows and self.width:
            kbd = self._wrap_kbd(kbd[0])
        return kbd

    def _wrap_kbd(self, kbd: List[InlineKeyboardButton]) -> List[List[InlineKeyboardButton]]:
        res: List[List[InlineKeyboardButton]] = []
        row: List[InlineKeyboardButton] = []
        for b in kbd:
            row.append(b)
            if len(row) >= self.width:
                res.append(row)
                row = []
        if row:
            res.append(row)
        return res

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager) -> bool:
        for b in self.buttons:
            if await b.process_callback(c, dialog, manager):
                return True
        return False


class Row(Group):
    def __init__(self, *buttons: Keyboard, id: Optional[str] = None, when: WhenCondition = None):
        super().__init__(*buttons, id=id, keep_rows=False, when=when)


class Column(Group):
    def __init__(self, *buttons: Keyboard, id: Optional[str] = None, when: WhenCondition = None):
        super().__init__(*buttons, id=id, keep_rows=False, when=when, width=1)
