from typing import Optional, Any, Protocol, Dict, Union

from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.storage import FSMContextProxy
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import MessageNotModified

from .intent import Data, Intent
from .stack import DialogStack
from ..data import DialogContext

ChatEvent = Union[CallbackQuery, Message]


class Dialog(Protocol):
    def register(self, dp: Dispatcher, *args, **kwargs):
        pass

    def states_group_name(self) -> str:
        pass

    def states_group(self) -> StatesGroup:
        pass

    async def start(self, manager: "DialogManager"):
        pass

    async def show(self, manager: "DialogManager"):
        pass

    async def process_result(self, result: Any, manager: "DialogManager"):
        pass


class DialogRegistry(Protocol):
    def find_dialog(self, state: Union[State, str]) -> Dialog:
        pass


async def remove_kbd_safe(event: ChatEvent, proxy: FSMContextProxy):
    if isinstance(event, CallbackQuery):
        await event.message.edit_reply_markup()
    else:
        stub_context = DialogContext(proxy, "", None)
        last_message_id = stub_context.last_message_id
        await event.bot.edit_message_reply_markup(event.chat.id, last_message_id)


class DialogManager:
    def __init__(
            self, event: ChatEvent, stack: DialogStack,
            proxy: FSMContextProxy, registry: DialogRegistry,
            data: Dict
    ):
        self.proxy = proxy
        self.stack = stack
        self.registry = registry
        self.event = event
        self.data = data
        self.context = self.load_context()

    async def start(self, state: State, data: Data = None):
        dialog = self.registry.find_dialog(state)
        self.stack.push(state.state, data)
        self.context = self.load_context()
        await dialog.start(self)

    async def done(self, result: Any = None, intent: Optional[Intent] = None):
        self.stack.pop(intent)
        self.context.clear()
        intent = self.current_intent()
        if intent:
            self.proxy.state = intent.name
        else:
            self.proxy.state = None
        dialog = self.dialog()
        self.context = self.load_context()
        if dialog:
            await dialog.process_result(result, self)
            await dialog.show(self)
        else:
            await remove_kbd_safe(self.event, self.proxy)

    async def close(self, intent: Intent):
        self.context.clear()
        self.stack.pop(intent)

    def current_intent(self) -> Intent:
        return self.stack.current()

    def dialog(self):
        current = self.current_intent()
        if not current:
            return None
        return self.registry.find_dialog(current.name)

    def load_context(self) -> Optional[DialogContext]:
        dialog = self.dialog()
        if not dialog:
            return None
        return DialogContext(self.proxy, dialog.states_group_name(), dialog.states_group())
