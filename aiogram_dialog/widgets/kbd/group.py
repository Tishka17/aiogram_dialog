from itertools import chain
from typing import List, Dict, Optional, Iterable

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.manager.manager import DialogManager, ManagedDialogProto
from .base import Keyboard
from ..when import WhenCondition


class Group(Keyboard):
    def __init__(self, *buttons: Keyboard, id: Optional[str] = None, width: int = None,
                 when: WhenCondition = None):
        super().__init__(id, when)
        self.buttons = buttons
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
            if self.width is None:
                kbd += b_kbd
            else:
                if not kbd:
                    kbd.append([])
                kbd[0].extend(chain.from_iterable(b_kbd))
        if self.width and kbd:
            kbd = self._wrap_kbd(kbd[0])
        return kbd

    def _wrap_kbd(
            self, kbd: Iterable[InlineKeyboardButton],
    ) -> List[List[InlineKeyboardButton]]:
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

    async def _process_other_callback(
            self, c: CallbackQuery, dialog: ManagedDialogProto,
            manager: DialogManager,
    ) -> bool:
        for b in self.buttons:
            if await b.process_callback(c, dialog, manager):
                return True
        return False


class Row(Group):
    def __init__(self, *buttons: Keyboard, id: Optional[str] = None, when: WhenCondition = None):
        super().__init__(*buttons, id=id, width=9999, when=when)  # telegram doe not allow even 100 columns


class Column(Group):
    def __init__(self, *buttons: Keyboard, id: Optional[str] = None, when: WhenCondition = None):
        super().__init__(*buttons, id=id, when=when, width=1)
