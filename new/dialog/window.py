from typing import Dict, Callable, Optional

from aiogram import Bot
from aiogram.dispatcher.filters.state import State
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery

from .dialog import Dialog, Window as WindowProtocol, DataGetter
from .kbd import Keyboard
from .text import Text


class Window(WindowProtocol):

    def __init__(self, text: Optional[Text], kbd: Optional[Keyboard], state: State,
                 getter: DataGetter = None,
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

    async def show(self, chat_id: int, user_id: int, dialog: Dialog, bot: Bot, data: Dict):
        current_data = await self.load_data(dialog, data)
        text = await self.render_text(current_data)
        kbd = await self.render_kbd(current_data)
        await bot.send_message(chat_id, text=text, reply_markup=kbd)

    def get_state(self) -> State:
        return self.state
