from typing import Optional, Any, Protocol

from aiogram import Dispatcher
from aiogram.dispatcher.storage import FSMContextProxy

from .intent import Data, Intent
from .registry import ChatEvent
from .stack import DialogStack


class Dialog(Protocol):
    def register(self, dp: Dispatcher, *args, **kwargs):
        pass

    def states_group_name(self) -> str:
        pass

    async def show(self, chat_event: ChatEvent, intent: Intent, data):
        pass

    async def process_result(self, chat_event: ChatEvent, result: Any, data):
        pass


class DialogRegistry(Protocol):
    def find_dialog(self, state: str) -> Dialog:
        pass


class DialogManager:
    def __init__(self, event: ChatEvent, stack: DialogStack, proxy: FSMContextProxy, registry: DialogRegistry):
        self.proxy = proxy
        self.stack = stack
        self.registry = registry
        self.event = event

    def start(self, name: str, data: Data, kwargs):
        dialog = self.registry.find_dialog(name)
        intent = self.stack.push(name, data)
        dialog.show(self.event, intent, kwargs)

    def done(self, kwargs, result: Any = None, intent: Optional[Intent] = None):
        self.stack.pop(intent)
        dialog = self.dialog()
        dialog.process_result(self.event, result, kwargs)
        dialog.show(self.event, self.stack.current(), kwargs)

    def close(self, intent: Intent):
        self.stack.pop(intent)

    def dialog(self):
        current = self.stack.current()
        return self.registry.find_dialog(current.name)
