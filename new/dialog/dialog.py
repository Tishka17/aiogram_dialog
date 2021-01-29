from typing import Dict, Callable, Awaitable, List, Union
from typing import Protocol

from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery, ContentTypes

from dialog.manager.manager import DialogManager

DIALOG_CONTEXT = "DIALOG_CONTEXT"
DataGetter = Callable[["Dialog", Dict], Awaitable[Dict]]

ChatEvent = Union[CallbackQuery, Message]


class Window(Protocol):
    async def render_text(self, data) -> str:
        raise NotImplementedError

    async def render_kbd(self, data) -> InlineKeyboardMarkup:
        raise NotImplementedError

    async def load_data(self, dialog: "Dialog", manager: DialogManager) -> Dict:
        raise NotImplementedError

    async def process_message(self, m: Message, dialog: "Dialog", manager: DialogManager):
        raise NotImplementedError

    async def process_callback(self, c: CallbackQuery, dialog: "Dialog", manager: DialogManager):
        raise NotImplementedError

    async def show(self, dialog: "Dialog", manager: DialogManager) -> Message:
        raise NotImplementedError

    def get_state(self) -> State:
        raise NotImplementedError


class Dialog:
    def __init__(self, *windows: Window):
        self._states_group = windows[0].get_state().group
        for w in windows:
            if w.get_state().group != self._states_group:
                raise ValueError("All windows must be attached to same StatesGroup")

        self.states: List[State] = [w.get_state() for w in windows]
        self.windows: Dict[State, Window] = dict(zip(self.states, windows))

    async def next(self, manager: DialogManager):
        new_state = self.states[self.states.index(manager.context.state) + 1]
        await self.switch_to(new_state, manager)

    async def back(self, manager: DialogManager):
        new_state = self.states[self.states.index(manager.context.state) - 1]
        await self.switch_to(new_state, manager)

    async def start(self, manager: DialogManager):
        new_state = self.states[0]
        await self.switch_to(new_state, manager)

    async def switch_to(self, state: State, manager: DialogManager):
        manager.context.state = state
        await self.show(manager)

    async def _current_window(self, manager: DialogManager) -> Window:
        return self.windows[manager.context.state]

    async def show(self, manager: DialogManager):
        window = await self._current_window(manager)
        message = await window.show(self, manager)
        manager.context.last_message_id = message.message_id

    async def _message_handler(self, m: Message, dialog_manager: DialogManager):
        window = await self._current_window(dialog_manager)
        await window.process_message(m, self, dialog_manager)

    async def _callback_handler(self, c: CallbackQuery, dialog_manager: DialogManager):
        window = await self._current_window(dialog_manager)
        await window.process_callback(c, self, dialog_manager)
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
