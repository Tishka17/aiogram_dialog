from logging import getLogger
from typing import Any, Optional, Dict

from aiogram.dispatcher.filters.state import State
from aiogram.types import User, Chat, Message, CallbackQuery, Document

from .bg_manager import BgManager
from .protocols import DialogManager, BaseDialogManager
from .protocols import ManagedDialogProto, DialogRegistryProto, NewMessage
from ..context.context import Context
from ..context.events import ChatEvent, StartMode, Data
from ..context.intent_filter import CONTEXT_KEY, STORAGE_KEY, STACK_KEY
from ..context.stack import Stack, DEFAULT_STACK_ID
from ..context.storage import StorageProxy
from ..exceptions import IncorrectBackgroundError
from ..utils import get_chat, remove_kbd, show_message

logger = getLogger(__name__)


class ManagerImpl(DialogManager):
    def __init__(self, event: ChatEvent, registry: DialogRegistryProto, data: Dict):
        self.disabled = False
        self._registry = registry
        self.event = event
        self.data = data
        self.force_new: Optional[bool] = None

    @property
    def registry(self) -> DialogRegistryProto:
        return self._registry

    def check_disabled(self):
        if self.disabled:
            raise IncorrectBackgroundError(
                "Detected background access to dialog manager. "
                "Please use background manager available via `manager.bg()` "
                "method to access methods from background tasks"
            )

    def dialog(self) -> ManagedDialogProto:
        self.check_disabled()
        current = self.current_context()
        if not current:
            raise RuntimeError
        return self.registry.find_dialog(current.state)

    def current_context(self) -> Optional[Context]:
        return self.data[CONTEXT_KEY]

    def current_stack(self) -> Optional[Stack]:
        return self.data[STACK_KEY]

    def storage(self) -> StorageProxy:
        return self.data[STORAGE_KEY]

    async def _remove_kbd(self) -> None:
        chat = get_chat(self.event)
        message = Message(chat=chat, message_id=self.current_stack().last_message_id)
        await remove_kbd(self.event.bot, message)
        self.current_stack().last_message_id = None

    async def done(self, result: Any = None) -> None:
        await self.dialog().process_close(result, self)
        old_context = self.current_context()
        await self.mark_closed()
        context = self.current_context()
        if not context:
            await self._remove_kbd()
            return
        dialog = self.dialog()
        await dialog.process_result(old_context.start_data, result, self)
        if context.id == self.current_context().id:
            await self.dialog().show(self)

    async def mark_closed(self) -> None:
        self.check_disabled()
        storage = self.storage()
        stack = self.current_stack()
        await storage.remove_context(stack.pop())
        if stack.empty():
            self.data[CONTEXT_KEY] = None
        else:
            intent_id = stack.last_intent_id()
            self.data[CONTEXT_KEY] = await storage.load_context(intent_id)

    async def start(
            self,
            state: State,
            data: Data = None,
            mode: StartMode = StartMode.NORMAL,
    ) -> None:
        self.check_disabled()
        storage = self.storage()
        if mode is StartMode.NORMAL:
            await self.storage().save_context(self.current_context())
            stack = self.current_stack()
            context = stack.push(state, data)
            self.data[CONTEXT_KEY] = context
            await self.dialog().process_start(self, data, state)
            if context.id == self.current_context().id:
                await self.dialog().show(self)
        elif mode is StartMode.RESET_STACK:
            stack = self.current_stack()
            while not stack.empty():
                await storage.remove_context(stack.pop())
            await self._remove_kbd()
            return await self.start(state, data, StartMode.NORMAL)
        elif mode is StartMode.NEW_STACK:
            stack = Stack()
            await self.bg(stack_id=stack.id).start(state, data, StartMode.NORMAL)
        else:
            raise ValueError(f"Unknown start mode: {mode}")

    async def switch_to(self, state: State) -> None:
        self.check_disabled()
        context = self.current_context()
        if context.state.group != state.group:
            raise ValueError(f"Cannot switch to another state group. "
                             f"Current state: {context.state}, asked for {state}")
        context.state = state

    async def show(self, new_message: NewMessage) -> Message:
        stack = self.current_stack()
        if (
                isinstance(self.event, CallbackQuery)
                and self.event.message
                and stack.last_message_id == self.event.message.message_id
        ):
            old_message = self.event.message
        else:
            if stack and stack.last_message_id:
                if stack.last_media_id:
                    # we create document beeasue
                    # * there is no method to set content type explicitly
                    # * we don't really care fo exact content type
                    document = Document(file_id=stack.last_media_id)
                    text = None
                else:
                    document = None
                    # we set some non empty-text which is not equal to anything
                    text = object()
                old_message = Message(message_id=stack.last_message_id,
                                      document=document,
                                      text=text,
                                      chat=get_chat(self.event))
            else:
                old_message = None
        if new_message.force_new is None:
            new_message.force_new = self._force_new()
        res = await show_message(self.event.bot, new_message, old_message)
        if isinstance(self.event, Message):
            stack.last_income_media_group_id = self.event.media_group_id
        self.force_new = False
        return res

    def _force_new(self) -> bool:
        if self.force_new is not None:
            return self.force_new
        if isinstance(self.event, Message):
            if self.event.media_group_id is None:
                return True
            return self.event.media_group_id != self.current_stack().last_income_media_group_id

    async def update(self, data: Dict) -> None:
        self.current_context().dialog_data.update(data)
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

        same_chat = (user.id == self.event.from_user.id and chat.id == get_chat(self.event).id)
        intent_id = None
        if stack_id is None:
            if same_chat:
                stack_id = self.current_stack().id
                if self.current_context():
                    intent_id = self.current_context().id
            else:
                stack_id = DEFAULT_STACK_ID
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
        del self._registry
        del self.event
        del self.data
