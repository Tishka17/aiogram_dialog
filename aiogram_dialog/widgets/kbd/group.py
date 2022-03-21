from itertools import chain, accumulate
from operator import itemgetter
from typing import List, Dict, Optional, Sequence, Union, Callable

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from .base import Keyboard
from ..when import WhenCondition

ItemsGetter = Callable[[Dict], Sequence]


def get_identity(items: Sequence) -> ItemsGetter:
    def identity(data) -> Sequence:
        return items
    return identity


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
            if self.width is None or not kbd:
                kbd += b_kbd
            else:
                kbd[0].extend(chain.from_iterable(b_kbd))
        if self.width and kbd:
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


class Layout(Keyboard):
    def __init__(self,
                 *buttons: Keyboard,
                 id: Optional[str] = None,
                 layout: Union[str, Sequence] = None,
                 when: WhenCondition = None):
        super().__init__(id, when)
        self.buttons = buttons

        if isinstance(layout, str):
            self.layout_getter = itemgetter(layout)
        elif layout is None:
            self.layout_getter = lambda x: None
        else:
            self.layout_getter = get_identity(layout)

    def find(self, widget_id):
        widget = super(Layout, self).find(widget_id)
        if widget:
            return widget
        for btn in self.buttons:
            widget = btn.find(widget_id)
            if widget:
                return widget
        return None

    async def _render_keyboard(self, data: Dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        kbd: List[List[InlineKeyboardButton]] = []
        layout = self.layout_getter(data)

        for b in self.buttons:
            b_kbd = await b.render_keyboard(data, manager)
            if layout is None or not kbd:
                kbd += b_kbd
            else:
                kbd[0].extend(chain.from_iterable(b_kbd))

        if layout and kbd:
            kbd = list(self._wrap_kbd(kbd[0], layout))
        return kbd

    def _wrap_kbd(self, kbd: List[InlineKeyboardButton], layout: Sequence) -> List[List[InlineKeyboardButton]]:
        _layout = list(accumulate(layout))

        for start, end in zip([0, *_layout],
                              [*_layout, _layout[-1]]):
            yield kbd[start:end]

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager) -> bool:
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
