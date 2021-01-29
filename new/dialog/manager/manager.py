from typing import Optional, Any, Protocol, Dict

from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.dispatcher.storage import FSMContextProxy

from .intent import Data, Intent
from .registry import ChatEvent
from .stack import DialogStack
from ..data import DialogContext


class Dialog(Protocol):
    def register(self, dp: Dispatcher, *args, **kwargs):
        pass

    def states_group_name(self) -> str:
        pass

    def states_group(self) -> StatesGroup:
        pass

    async def start(self, chat_event: ChatEvent, intent: Intent, data: Dict):
        pass

    async def show(self, chat_event: ChatEvent, intent: Intent, data: Dict):
        pass

    async def process_result(self, chat_event: ChatEvent, result: Any, data: Dict):
        pass


class DialogRegistry(Protocol):
    def find_dialog(self, state: str) -> Dialog:
        pass


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

    def start(self, name: str, data: Data):
        dialog = self.registry.find_dialog(name)
        intent = self.stack.push(name, data)
        self.context = self.load_context()
        dialog.start(self.event, intent, self.data)

    def done(self, result: Any = None, intent: Optional[Intent] = None):
        self.stack.pop(intent)
        dialog = self.dialog()
        self.context.clear()
        self.context = self.load_context()
        dialog.process_result(self.event, result, self.data)
        dialog.show(self.event, self.stack.current(), self.data)

    def close(self, intent: Intent):
        self.context.clear()
        self.stack.pop(intent)

    def dialog(self):
        current = self.stack.current()
        return self.registry.find_dialog(current.name)

    def load_context(self) -> DialogContext:
        dialog = self.dialog()
        return DialogContext(self.proxy, dialog.states_group_name(), dialog.states_group())
