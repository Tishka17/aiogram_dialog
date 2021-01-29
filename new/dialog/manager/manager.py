from typing import Optional, Any, Protocol, Dict, Union

from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.storage import FSMContextProxy
from aiogram.types import CallbackQuery, Message

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
        intent = self.stack.push(state.state, data)
        self.context = self.load_context()
        await dialog.start(self)

    async def done(self, result: Any = None, intent: Optional[Intent] = None):
        self.stack.pop(intent)
        dialog = self.dialog()
        self.context.clear()
        self.context = self.load_context()
        await dialog.process_result(result, self)
        await dialog.show(self)

    async def close(self, intent: Intent):
        self.context.clear()
        self.stack.pop(intent)

    def dialog(self):
        current = self.stack.current()
        if not current:
            return None
        return self.registry.find_dialog(current.name)

    def load_context(self) -> Optional[DialogContext]:
        dialog = self.dialog()
        if not dialog:
            return None
        return DialogContext(self.proxy, dialog.states_group_name(), dialog.states_group())
