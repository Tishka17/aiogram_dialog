from typing import Optional, Any, Dict

from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.storage import FSMContextProxy
from aiogram.types import CallbackQuery, Chat, User, Message

from .bg_manager import BgManager
from .intent import Data, Intent, ChatEvent
from .protocols import DialogRegistryProto, DialogManager, BgManagerProto
from .stack import DialogStack
from ..data import DialogContext, reset_dialog_contexts
from ..utils import get_chat, remove_kbd


class IncorrectBackgroundError(RuntimeError):
    pass


class DialogManagerImpl(DialogManager):
    def __init__(
            self, event: ChatEvent, stack: DialogStack,
            proxy: FSMContextProxy, registry: DialogRegistryProto,
            data: Dict
    ):
        self.disabled = False
        self.proxy = proxy
        self.stack = stack
        self.registry = registry
        self.event = event
        self.data = data
        self.context = self.load_context()

    def check_disabled(self):
        if self.disabled:
            raise IncorrectBackgroundError(
                "Detected background access to dialog manager. "
                "Please use background manager available via `manager.bg()` "
                "method to access methods from background tasks"
            )

    async def _remove_kbd(self) -> None:
        chat = get_chat(self.event)
        if isinstance(self.event, CallbackQuery):
            message = self.event.message
        else:
            stub_context = DialogContext(self.proxy, "", None)
            if not stub_context.last_message_id:
                return
            message = Message(chat=chat, message_id=stub_context.last_message_id)
        await remove_kbd(self.event.bot, message)

    async def start(self, state: State, data: Data = None, reset_stack: bool = False):
        self.check_disabled()
        if reset_stack:
            await self._remove_kbd()
            reset_dialog_contexts(self.proxy)
            self.stack.clear()
        dialog = self.registry.find_dialog(state)
        self.stack.push(state.state, data)
        self.context = self.load_context()
        await dialog.process_start(self, data, state)

    async def done(self, result: Any = None):
        self.check_disabled()
        await self.dialog().process_close(result, self)
        await self.mark_closed()
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
            await self._remove_kbd()

    async def mark_closed(self):
        self.check_disabled()
        if self.context:
            self.context.clear()
        self.stack.pop()

    def current_intent(self) -> Intent:
        self.check_disabled()
        return self.stack.current()

    def dialog(self):
        self.check_disabled()
        current = self.current_intent()
        if not current:
            return None
        return self.registry.find_dialog(current.name)

    def load_context(self) -> Optional[DialogContext]:
        self.check_disabled()
        dialog = self.dialog()
        if not dialog:
            return None
        return DialogContext(self.proxy, dialog.states_group_name(), dialog.states_group())

    async def switch_to(self, state):
        self.check_disabled()
        self.context.state = state

    def bg(self, user_id: Optional[int] = None, chat_id: Optional[int] = None) -> BgManagerProto:
        if self.disabled:
            raise IncorrectBackgroundError(
                "Please call `manager.bg()` "
                "before starting background task"
            )
        self.check_disabled()

        if user_id is not None:
            user = User(id=user_id)
        else:
            user = self.event.from_user
        if chat_id is not None:
            chat = Chat(id=chat_id)
        else:
            chat = get_chat(self.event)

        return BgManager(
            user,
            chat,
            self.event.bot,
            self.registry,
            self.current_intent(),
            self.context.state,
        )

    async def close_manager(self) -> None:
        await self.proxy.save()
        self.disabled = True
        del self.proxy
        del self.stack
        del self.registry
        del self.event
        del self.data
        del self.context
