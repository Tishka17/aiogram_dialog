from typing import Dict, Callable, Awaitable, List, Union
from typing import Protocol

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery, ContentTypes

from dialog.manager.manager import DialogManager
from .data import DialogContext

DIALOG_CONTEXT = "DIALOG_CONTEXT"
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

    async def show(self, chat_event: ChatEvent, dialog: "Dialog", data: Dict) -> Message:
        raise NotImplementedError

    def get_state(self) -> State:
        raise NotImplementedError


class Dialog:
    def __init__(self, *windows: Window):
        self._states_group = windows[0].get_state().group
        for w in windows:
            if w.get_state().group != self._states_group:
                raise ValueError("All windows must be attached to same StatesGroup")

        self.states: List[str] = [w.get_state().state for w in windows]
        self.windows: Dict[str, Window] = dict(zip(self.states, windows))

    async def next(self, chat_event: ChatEvent, data: Dict):
        state: FSMContext = data["state"]
        current_state = await state.get_state()
        new_state = self.states[self.states.index(current_state) + 1]
        await self.switch_to(new_state, chat_event, data)

    async def context(self, data):
        context = data.get(DIALOG_CONTEXT)
        if not context:
            manager: DialogManager = data["dialog_manager"]
            context = DialogContext(manager.proxy, self.states_group_name())
            data[DIALOG_CONTEXT] = context
        return context

    async def back(self, chat_event: ChatEvent, data: Dict):
        context = await self.context(data)
        new_state = self.states[self.states.index(context.state) - 1]
        await self.switch_to(new_state, chat_event, data)

    async def start(self, chat_event: ChatEvent, data: Dict):
        new_state = self.states[0]
        await self.switch_to(new_state, chat_event, data)

    async def switch_to(self, state: str, chat_event: ChatEvent, data: Dict):
        context = await self.context(data)
        context.state = state
        await self.show(chat_event, data)

    async def _current_window(self, data) -> Window:
        context = await self.context(data)
        return self.windows[context.state]

    async def show(self, chat_event: ChatEvent, data):
        context = await self.context(data)
        window = await self._current_window(data)
        message = await window.show(chat_event, self, data)
        context.last_message_id = message.message_id

    async def _message_handler(self, m: Message, **kwargs):
        context = await self.context(kwargs)
        window = await self._current_window(kwargs)
        await window.process_message(m, self, kwargs)

    async def _callback_handler(self, c: CallbackQuery, **kwargs):
        context = await self.context(kwargs)
        window = await self._current_window(kwargs)
        await window.process_callback(c, self, kwargs)
        await c.answer()

    def register(self, dp: Dispatcher, **filters):
        dp.register_callback_query_handler(self._callback_handler, state=self.states, **filters)
        if "content_types" not in filters:
            filters["content_types"] = ContentTypes.ANY
        dp.register_message_handler(self._message_handler, state=self.states, **filters)

    def states_group(self) -> StatesGroup:
        return self._states_group

    def states_group_name(self) -> str:
        return self._states_group.__full_group_name__
