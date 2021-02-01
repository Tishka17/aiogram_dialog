from itertools import chain
from typing import List, Callable, Union

from aiogram.types import InlineKeyboardButton, CallbackQuery

from dialog.dialog import Dialog
from dialog.manager.manager import DialogManager
from .base import Keyboard


class Group(Keyboard):
    def __init__(self, *buttons: Keyboard, keep_rows: bool = True, width: int = 0,
                 when: Union[str, Callable, None] = None):
        super().__init__(when)
        self.buttons = buttons
        self.keep_rows = keep_rows
        self.width = width

    async def _render_kbd(self, data) -> List[List[InlineKeyboardButton]]:
        kbd: List[List[InlineKeyboardButton]] = []
        for b in self.buttons:
            b_kbd = await b.render_kbd(data)
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


def Row(*buttons: Keyboard, when: Union[str, Callable, None] = None):
    return Group(*buttons, keep_rows=False, when=when)
