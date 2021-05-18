from logging import getLogger
from typing import Any, Optional, Dict

from aiogram.dispatcher.filters.state import State
from aiogram.types import User, Chat, CallbackQuery, Message

from .bg_manager import BgManager
from .protocols import DialogManager, BaseDialogManager
from .protocols import ManagedDialogProto, DialogRegistryProto
from ..context.context_compat import ContextCompat
from ..context.events import ChatEvent, StartMode
from ..context.intent import Intent, Data
from ..context.intent_filter import INTENT_KEY, STORAGE_KEY, STACK_KEY
from ..context.stack import Stack
from ..context.storage import StorageProxy
from ..utils import get_chat, remove_kbd

logger = getLogger(__name__)


class IncorrectBackgroundError(RuntimeError):
    pass


class ManagerImpl(DialogManager):
    def __init__(self, event: ChatEvent, registry: DialogRegistryProto, data: Dict):
        self.disabled = False
        self.registry = registry
        self.event = event
        self.data = data

    @property
    def context(self) -> Optional[ContextCompat]:
        if not self.current_stack():
            return None
        return ContextCompat(
            self.current_intent(),
            self.current_stack(),
        )

    def check_disabled(self):
        if self.disabled:
            raise IncorrectBackgroundError(
                "Detected background access to dialog manager. "
                "Please use background manager available via `manager.bg()` "
                "method to access methods from background tasks"
            )

    def dialog(self) -> ManagedDialogProto:
        self.check_disabled()
        current = self.current_intent()
        if not current:
            raise RuntimeError
        return self.registry.find_dialog(current.state)

    def current_intent(self) -> Optional[Intent]:
        return self.data[INTENT_KEY]

    def current_stack(self) -> Optional[Stack]:
        return self.data[STACK_KEY]

    def storage(self) -> StorageProxy:
        return self.data[STORAGE_KEY]

    async def _remove_kbd(self) -> None:
        chat = get_chat(self.event)
        if isinstance(self.event, CallbackQuery):
            message = self.event.message
        else:
            message = Message(chat=chat, message_id=self.current_stack().last_message_id)
        await remove_kbd(self.event.bot, message)
        self.current_stack().last_message_id = None

    async def done(self, result: Any = None) -> None:
        await self.dialog().process_close(result, self)
        await self.mark_closed()
        intent = self.current_intent()
        if not intent:
            await self._remove_kbd()
            return
        dialog = self.dialog()
        await dialog.process_result(result, self)
        await dialog.show(self)  # TODO remove stack if empty

    async def mark_closed(self) -> None:
        self.check_disabled()
        storage = self.storage()
        stack = self.current_stack()
        await storage.remove_intent(stack.pop())
        if stack.empty():
            self.data[INTENT_KEY] = None
        else:
            intent_id = stack.last_intent_id()
            self.data[INTENT_KEY] = await storage.load_intent(intent_id)

    async def start(
            self,
            state: State,
            data: Data = None,
            mode: StartMode = StartMode.NORMAL,
    ) -> None:
        self.check_disabled()
        storage = self.storage()
        if mode is StartMode.NORMAL:
            await self.storage().save_intent(self.current_intent())
            stack = self.current_stack()
            intent = stack.push(state, data)
            self.data[INTENT_KEY] = intent
            await self.dialog().process_start(self, data, state)
        elif mode is StartMode.RESET:
            stack = self.current_stack()
            while not stack.empty():
                await storage.remove_intent(stack.pop())
            return await self.start(state, data, StartMode.NORMAL)
        elif mode is StartMode.NEW_STACK:
            stack = Stack()
            await self.bg(stack_id=stack.id).start(state, data, StartMode.NORMAL)
        else:
            raise ValueError(f"Unknown start mode: {mode}")

    async def switch_to(self, state: State) -> None:
        self.check_disabled()
        intent = self.current_intent()
        if intent.state.group != state.group:
            raise ValueError(f"Cannot switch to another state group. "
                             f"Current state: {intent.state}, asked for {state}")
        intent.state = state

    async def update(self, data: Dict) -> None:
        self.current_intent().dialog_data.update(data)
        await self.dialog().show(self)

    def bg(
            self,
            user_id: Optional[int] = None,
            chat_id: Optional[int] = None,
            stack_id: Optional[str] = None,
    ) -> "BaseDialogManager":
        if user_id is not None:
            user = User(id=user_id)
        else:
            user = self.event.from_user
        if chat_id is not None:
            chat = Chat(id=chat_id)
        else:
            chat = get_chat(self.event)

        intent_id = None
        if stack_id is None:
            stack_id = self.current_stack().id
            if not self.current_stack().empty():
                intent_id = self.current_intent().id

        return BgManager(
            user=user,
            chat=chat,
            bot=self.event.bot,
            registry=self.registry,
            intent_id=intent_id,
            stack_id=stack_id,
        )

    async def close_manager(self) -> None:
        self.check_disabled()
        self.disabled = True
        del self.registry
        del self.event
        del self.data
