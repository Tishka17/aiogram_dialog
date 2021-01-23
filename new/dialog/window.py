from typing import Dict, Callable, Optional

from aiogram.dispatcher.filters.state import State
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery

from .dialog import Dialog, Window as WindowProtocol, DataGetter
from .kbd import Keyboard
from .text import Text


class Window(WindowProtocol):

    def __init__(self, text: Text, kbd: Keyboard, getter: DataGetter, state: State,
                 on_message: Optional[Callable] = None):
        self.text = text
        self.kbd = kbd
        self.getter = getter
        self.state = state
        self.on_message = on_message

    async def render_text(self, data) -> str:
        return await self.text.render_text(data)

    async def render_kbd(self, data) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=await self.kbd.render_kbd(data)
        )

    async def load_data(self, dialog: "Dialog", data: Dict) -> Dict:
        if not self.getter:
            return {}
        return await self.getter(dialog, data)

    async def process_message(self, m: Message, dialog: Dialog, data: Dict):
        if self.on_message:
            await self.on_message(m, dialog, data)

    async def process_callback(self, c: CallbackQuery, dialog: Dialog, data: Dict):
        if self.kbd:
            await self.kbd.process_callback(c, dialog, data)

    def get_state(self) -> State:
        return self.state
