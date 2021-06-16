from itertools import chain, zip_longest
from typing import List, Dict, Optional, Any, Tuple, TypeVar, Generic

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.text import Const

from .button import Button
from .base import Keyboard
from ..when import WhenCondition


# Constants for navigating pages with buttons
PAGE_FIRST = "0"
PAGE_LAST = "-1"
PAGE_NEXT = "+"
PAGE_PREV = "-"

T = TypeVar("T")


class BiDirCollection(Generic[T]):
    def __init__(self, collection):
        self.collection = collection
        self.current_index = 0
        self.last_index = len(collection) - 1

    def current_state(self):
        return self.collection[self.current_index]

    def first(self) -> None:
        self.current_index = 0

    def next(self) -> T:
        if self.current_index < self.last_index:
            self.current_index += 1
        return self.collection[self.current_index]

    def prev(self) -> T:
        if self.current_index == 0:
            return self.collection[self.current_index]
        self.current_index -= 1
        return self.collection[self.current_index]

    def last(self) -> None:
        self.current_index = self.last_index

    def __iter__(self):
        return self


def btns_to_chunks(collection: List[Any],
                   n: int) -> List[Tuple[Any]]:
    fillvalue = Button(Const(" "), id="")
    iterator = [iter(collection)] * n
    chunks = zip_longest(fillvalue=fillvalue, *iterator)
    return list(chunks)


class ScrollingGroup(Keyboard):
    def __init__(self, *buttons: Keyboard,
                 id: Optional[str] = None,
                 keep_rows: bool = False,
                 width: int = 0,
                 height: int = 0,
                 when: WhenCondition = None):
        super().__init__(id, when)
        self.keep_rows = keep_rows
        self.width = width
        self.height = height
        self.btn_per_page = self.width * self.height
        self.btn_pages = btns_to_chunks([*buttons], self.btn_per_page)
        self.btn_pages_iterator = BiDirCollection(self.btn_pages)

    def find(self, widget_id):
        widget = super(ScrollingGroup, self).find(widget_id)
        if widget:
            return widget
        for btn in self.btn_pages_iterator.current_state():
            widget = btn.find(widget_id)
            if widget:
                return widget
        return None

    async def _render_keyboard(self, data: Dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        kbd: List[List[InlineKeyboardButton]] = []
        for b in self.btn_pages_iterator.current_state():
            b_kbd = await b.render_keyboard(data, manager)
            if self.keep_rows or not kbd:
                kbd += b_kbd
            else:
                kbd[0].extend(chain.from_iterable(b_kbd))
        if not self.keep_rows and self.width:
            kbd = self._wrap_kbd(kbd[0])

        kbd.append(self.scrolling())
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

    def scrolling(self):
        last_page_index = str(self.btn_pages_iterator.last_index + 1)
        current_page_index = str(self.btn_pages_iterator.current_index + 1)
        return [
            InlineKeyboardButton(text="1", callback_data=f"{self.widget_id}:{PAGE_FIRST}"),
            InlineKeyboardButton(text="<", callback_data=f"{self.widget_id}:{PAGE_PREV}"),
            InlineKeyboardButton(text=current_page_index, callback_data=" "),
            InlineKeyboardButton(text=">", callback_data=f"{self.widget_id}:{PAGE_NEXT}"),
            InlineKeyboardButton(text=last_page_index, callback_data=f"{self.widget_id}:{PAGE_LAST}"),
        ]

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager) -> bool:
        prefix = f"{self.widget_id}:"
        data = c.data[len(prefix):]

        if data == PAGE_NEXT:
            self.btn_pages_iterator.next()
        elif data == PAGE_PREV:
            self.btn_pages_iterator.prev()
        elif data == PAGE_FIRST:
            self.btn_pages_iterator.first()
        elif data == PAGE_LAST:
            self.btn_pages_iterator.last()
        for b in self.btn_pages_iterator.current_state():
            if await b.process_callback(c, dialog, manager):
                return True
        return False
