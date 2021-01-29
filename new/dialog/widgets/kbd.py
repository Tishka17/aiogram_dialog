from itertools import chain
from typing import List, Callable, Optional, Union

from aiogram.dispatcher.filters.state import State
from aiogram.types import InlineKeyboardButton, CallbackQuery

from dialog.dialog import Dialog
from .text import Text, Const
from .when import Whenable
from ..manager.manager import DialogManager


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


class Button(Keyboard):
    def __init__(self, text: Text, callback_data: str, on_click: Optional[Callable] = None,
                 when: Union[str, Callable] = None):
        super().__init__(when)
        self.text = text
        self.callback_data = callback_data
        self.on_click = on_click

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager) -> bool:
        if c.data != self.callback_data:
            return False
        if self.on_click:
            await self.on_click(c, dialog, manager)
        return True

    async def _render_kbd(self, data) -> List[List[InlineKeyboardButton]]:
        return [[
            InlineKeyboardButton(
                text=await self.text.render_text(data),
                callback_data=self.callback_data
            )
        ]]


class SwitchState(Button):
    def __init__(self, text: Text, callback_data: str,
                 state: State,
                 on_click: Optional[Callable] = None,
                 when: Union[str, Callable] = None):
        super().__init__(text, callback_data, self._on_click, when)
        self.text = text
        self.callback_data = callback_data
        self.user_on_click = on_click
        self.state = state.state

    async def _on_click(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, dialog, manager)
        await dialog.switch_to(self.state, manager)


class Next(Button):
    def __init__(self, text: Text = Const("Next"), callback_data: str = "next",
                 on_click: Optional[Callable] = None,
                 when: Union[str, Callable] = None):
        super().__init__(text, callback_data, self._on_click, when)
        self.text = text
        self.callback_data = callback_data
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, dialog, manager)
        await dialog.next(manager)


class Back(Button):
    def __init__(self, text: Text = Const("Back"), callback_data: str = "back",
                 on_click: Optional[Callable] = None,
                 when: Union[str, Callable] = None):
        super().__init__(text, callback_data, self._on_click, when)
        self.text = text
        self.callback_data = callback_data
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, dialog, manager)
        await dialog.back(manager)


class Cancel(Button):
    def __init__(self, text: Text = Const("Cancel"), callback_data: str = "cancel",
                 on_click: Optional[Callable] = None,
                 when: Union[str, Callable] = None):
        super().__init__(text, callback_data, self._on_click, when)
        self.text = text
        self.callback_data = callback_data
        self.user_on_click = on_click

    async def _on_click(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, dialog, manager)
        await manager.done()


class Uri(Keyboard):
    def __init__(self, text: Text, uri: Text, when: Union[str, Callable, None] = None):
        super().__init__(when)
        self.text = text
        self.uri = uri

    async def _render_kbd(self, data) -> List[List[InlineKeyboardButton]]:
        return [[
            InlineKeyboardButton(
                text=await self.text.render_text(data),
                uri=await self.uri.render_text(data)
            )
        ]]


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
