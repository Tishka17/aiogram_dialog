from collections.abc import Iterable
from itertools import chain

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog.api.internal import ButtonVariant, RawKeyboard
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import WhenCondition
from .base import Keyboard


class Group(Keyboard):
    def __init__(
            self,
            *buttons: Keyboard,
            id: str | None = None,
            width: int | None = None,
            width_symbols: int | None = None,
            when: WhenCondition = None,
    ):
        super().__init__(id=id, when=when)
        if width is not None and width_symbols is not None:
            raise ValueError(
                "Only one of `width` and `width_symbols` can be set",
            )
        self.buttons = buttons
        self.width = width
        self.width_symbols = width_symbols

    def find(self, widget_id):
        widget = super().find(widget_id)
        if widget:
            return widget
        for btn in self.buttons:
            widget = btn.find(widget_id)
            if widget:
                return widget
        return None

    async def _render_keyboard(
            self,
            data: dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        kbd: RawKeyboard = []
        for b in self.buttons:
            b_kbd = await b.render_keyboard(data, manager)
            if self.width is None and self.width_symbols is None:
                kbd += b_kbd
            else:
                if not kbd:
                    kbd.append([])
                kbd[0].extend(chain.from_iterable(b_kbd))
        if (self.width or self.width_symbols) and kbd:
            kbd = self._wrap_kbd(kbd[0])
        return kbd

    def _wrap_kbd(
            self,
            kbd: Iterable[InlineKeyboardButton],
    ) -> RawKeyboard:
        if self.width_symbols:
            return self._wrap_kbd_by_symbols(kbd)
        return self._wrap_kbd_by_width(kbd)

    def _wrap_kbd_by_width(
            self,
            kbd: Iterable[InlineKeyboardButton],
    ) -> RawKeyboard:
        res: RawKeyboard = []
        row: list[ButtonVariant] = []
        for b in kbd:
            row.append(b)
            if len(row) >= self.width:
                res.append(row)
                row = []
        if row:
            res.append(row)
        return res

    def _wrap_kbd_by_symbols(
            self,
            kbd: Iterable[InlineKeyboardButton],
    ) -> RawKeyboard:
        res: RawKeyboard = []
        row: list[ButtonVariant] = []
        row_len = 0
        for b in kbd:
            b_len = len(b.text)
            # only wrap a non-empty row, so an over-long button keeps its row
            if row and row_len + b_len > self.width_symbols:
                res.append(row)
                row = []
                row_len = 0
            row.append(b)
            row_len += b_len
        if row:
            res.append(row)
        return res

    async def _process_other_callback(
            self,
            callback: CallbackQuery,
            dialog: DialogProtocol,
            manager: DialogManager,
    ) -> bool:
        for b in self.buttons:
            if await b.process_callback(callback, dialog, manager):
                return True
        return False


class Row(Group):
    def __init__(
            self,
            *buttons: Keyboard,
            id: str | None = None,
            when: WhenCondition = None,
    ):
        super().__init__(
            *buttons, id=id, width=9999, when=when,
        )  # telegram doe not allow even 100 columns


class Column(Group):
    def __init__(
            self,
            *buttons: Keyboard,
            id: str | None = None,
            when: WhenCondition = None,
    ):
        super().__init__(*buttons, id=id, when=when, width=1)
