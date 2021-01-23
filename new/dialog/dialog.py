from typing import Dict, Callable, Awaitable
from typing import Protocol

from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery, ContentTypes

DataGetter = Callable[["Dialog", Dict], Awaitable[Dict]]


class Window(Protocol):
    async def render_text(self, data) -> str:
        raise NotImplementedError

    async def render_kbd(self, data) -> InlineKeyboardMarkup:
        raise NotImplementedError

    async def load_data(self, dialog: "Dialog", data: Dict) -> Dict:
        raise NotImplementedError

    async def process_message(self, m: Message, dialog: "Dialog", data: Dict):
        raise NotImplementedError

    async def process_callback(self, c: CallbackQuery, dialog: "Dialog", data: Dict):
        raise NotImplementedError

    def get_state(self) -> State:
        raise NotImplementedError


class Dialog:
    def __init__(self, *windows: Window):
        self.states = [w.get_state().state for w in windows]
        self.windows: Dict[str, Window] = dict(zip(self.states, windows))

    async def show(self, bot: Bot, chat_id: int, data):
        state: FSMContext = data["state"]
        current_state = await state.get_state()
        window = self.windows[current_state]

        current_data = await window.load_data(self, data)
        text = await window.render_text(current_data)
        kbd = await window.render_kbd(current_data)
        await bot.send_message(chat_id, text=text, reply_markup=kbd)

    async def _message_handler(self, m: Message, **kwargs):
        state: FSMContext = kwargs["state"]
        current_state = await state.get_state()
        window = self.windows[current_state]
        await window.process_message(m, self, kwargs)

    async def _callback_handler(self, c: CallbackQuery, **kwargs):
        state: FSMContext = kwargs["state"]
        current_state = await state.get_state()
        window = self.windows[current_state]
        await window.process_callback(c, self, kwargs)
        await c.answer()

    def register(self, dp: Dispatcher, **filters):
        dp.register_callback_query_handler(self._callback_handler, state=self.states, **filters)
        if "content_types" not in filters:
            filters["content_types"] = ContentTypes.ANY
        dp.register_message_handler(self._message_handler, state=self.states, **filters)
