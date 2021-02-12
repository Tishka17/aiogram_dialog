from typing import Optional, Any, Dict, Protocol, Type

from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContextProxy
from aiogram.types import CallbackQuery

from .bg_manager import BgManager
from .intent import Data, Intent, ChatEvent
from .protocols import DialogRegistryProto, DialogManager, BgManagerProto
from .stack import DialogStack
from ..data import DialogContext, reset_dialog_contexts


async def remove_kbd_safe(event: ChatEvent, proxy: FSMContextProxy):
    if isinstance(event, CallbackQuery):
        await event.message.edit_reply_markup()
    else:
        stub_context = DialogContext(proxy, "", None)
        last_message_id = stub_context.last_message_id
        if last_message_id:
            await event.bot.edit_message_reply_markup(event.chat.id, last_message_id)


class DialogManagerImpl(DialogManager):
    def __init__(
            self, event: ChatEvent, stack: DialogStack,
            proxy: FSMContextProxy, registry: DialogRegistryProto,
            data: Dict
    ):
        self.proxy = proxy
        self.stack = stack
        self.registry = registry
        self.event = event
        self.data = data
        self.context = self.load_context()

    async def start(self, state: State, data: Data = None, reset_stack: bool = False):
        if reset_stack:
            await remove_kbd_safe(self.event, self.proxy)
            reset_dialog_contexts(self.proxy)
            self.stack.clear()
        dialog = self.registry.find_dialog(state)
        self.stack.push(state.state, data)
        self.context = self.load_context()
        await dialog.start(self, state)

    async def done(self, result: Any = None):
        self.stack.pop()
        if self.context:
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

    async def close(self):
        self.context.clear()
        self.stack.pop()

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

    async def switch_to(self, state):
        self.context.state = state

    def bg(self) -> BgManagerProto:
        return BgManager(
            self.event,
            self.registry,
            self.current_intent(),
            self.context.state,
        )
