from typing import Dict
from typing import Protocol

from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery, ContentTypes


class Window(Protocol):
    async def render_text(self, data) -> str:
        raise NotImplementedError

    async def render_kbd(self, data) -> InlineKeyboardMarkup:
        raise NotImplementedError

    async def load_data(self) -> Dict:
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
        self.windows: Dict[State, Window] = dict(zip(self.states, windows))

    async def _message_handler(self, m: Message, **kwargs):
        state = kwargs["state"]
        window = self.windows[state]
        await window.process_message(m, self, kwargs)

    async def _callback_handler(self, c: CallbackQuery, **kwargs):
        state = kwargs["state"]
        window = self.windows[state]
        await window.process_callback(c, self, kwargs)

    def register(self, dp: Dispatcher, **filters):
        dp.register_callback_query_handler(self._callback_handler, state=self.states, **filters)
        if "content_types" not in filters:
            filters["content_types"] = ContentTypes.ANY
        dp.register_message_handler(self._message_handler, state=self.states, **filters)
