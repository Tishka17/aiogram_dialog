from typing import Dict, Callable

from aiogram.types import InlineKeyboardMarkup

from .kbd import Keyboard
from .text import Text


class Window:
    def __init__(self, text: Text, kbd: Keyboard, getter: Callable):
        self.text = text
        self.kbd = kbd
        self.getter = getter

    async def render_text(self, data) -> str:
        return await self.text.render_text(data)

    async def render_kbd(self, data) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=await self.kbd.render_kbd(data)
        )

    async def load_data(self) -> Dict:
        if not self.getter:
            return {}
        return await self.getter()