from typing import Dict, Callable, Awaitable, List, Union
from typing import Protocol

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery, ContentTypes

DataGetter = Callable[["Dialog", Dict], Awaitable[Dict]]

ChatEvent = Union[CallbackQuery, Message]


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

    async def show(self, chat_event: ChatEvent, dialog: "Dialog", data: Dict):
        raise NotImplementedError

    def get_state(self) -> State:
        raise NotImplementedError


class Dialog:
    def __init__(self, *windows: Window):
        self.states: List[str] = [w.get_state().state for w in windows]
        self.windows: Dict[str, Window] = dict(zip(self.states, windows))

    async def next(self, chat_event: ChatEvent, data: Dict):
        state: FSMContext = data["state"]
        current_state = await state.get_state()
        new_state = self.states[self.states.index(current_state) + 1]
        await self.switch_to(new_state, chat_event, data)

    async def back(self, chat_event: ChatEvent, data: Dict):
        state: FSMContext = data["state"]
        current_state = await state.get_state()
        new_state = self.states[self.states.index(current_state) - 1]
        await self.switch_to(new_state, chat_event, data)

    async def start(self, chat_event: ChatEvent, data: Dict):
        new_state = self.states[0]
        await self.switch_to(new_state, chat_event, data)

    async def switch_to(self, state: str, chat_event: ChatEvent, data: Dict):
        context: FSMContext = data["state"]
        await context.set_state(state)
        await self.show(chat_event, data)

    async def _current_window(self, data) -> Window:
        state: FSMContext = data["state"]
        current_state = await state.get_state()
        return self.windows[current_state]

    async def show(self, chat_event: ChatEvent, data):
        window = await self._current_window(data)
        await window.show(chat_event, self, data)

    async def _message_handler(self, m: Message, **kwargs):
        window = await self._current_window(kwargs)
        await window.process_message(m, self, kwargs)

    async def _callback_handler(self, c: CallbackQuery, **kwargs):
        window = await self._current_window(kwargs)
        await window.process_callback(c, self, kwargs)
        await c.answer()

    def register(self, dp: Dispatcher, **filters):
        dp.register_callback_query_handler(self._callback_handler, state=self.states, **filters)
        if "content_types" not in filters:
            filters["content_types"] = ContentTypes.ANY
        dp.register_message_handler(self._message_handler, state=self.states, **filters)
