from typing import List, Callable, Optional, Union, Dict, Awaitable

from aiogram.types import InlineKeyboardButton, CallbackQuery

from aiogram_dialog.dialog import Dialog
from aiogram_dialog.manager.manager import DialogManager
from aiogram_dialog.widgets.text import Text
from .base import Keyboard
from ..when import WhenCondition

OnClick = Callable[[CallbackQuery, "Button", DialogManager], Awaitable]


class Button(Keyboard):
    def __init__(self, text: Text, id: str, on_click: Optional[OnClick] = None,
                 when: WhenCondition = None):
        super().__init__(id, when)
        self.text = text
        self.on_click = on_click

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, manager: DialogManager) -> bool:
        if c.data != self.widget_id:
            return False
        if self.on_click:
            await self.on_click(c, self, manager)
        return True

    async def _render_kbd(self, data: Dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        return [[
            InlineKeyboardButton(
                text=await self.text.render_text(data, manager),
                callback_data=self.widget_id
            )
        ]]


class Url(Keyboard):
    def __init__(self, text: Text, url: Text, id: Optional[str] = None, when: Union[str, Callable, None] = None):
        super().__init__(id, when)
        self.text = text
        self.url = url

    async def _render_kbd(self, data: Dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        return [[
            InlineKeyboardButton(
                text=await self.text.render_text(data, manager),
                url=await self.url.render_text(data, manager)
            )
        ]]
