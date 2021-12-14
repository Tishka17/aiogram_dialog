from logging import getLogger
from typing import Any, Optional, Dict

from aiogram.dispatcher.filters.state import State
from aiogram.types import User, Chat, Message, CallbackQuery, Document

from .bg_manager import BgManager
from .dialog import ManagedDialogAdapter
from .protocols import (
    DialogManager, BaseDialogManager, ShowMode, LaunchMode,
    ManagedDialogAdapterProto, ManagedDialogProto, DialogRegistryProto,
    NewMessage,
)
from ..context.context import Context
from ..context.events import ChatEvent, StartMode, Data
from ..context.intent_filter import CONTEXT_KEY, STORAGE_KEY, STACK_KEY
from ..context.stack import Stack, DEFAULT_STACK_ID
from ..context.storage import StorageProxy
from ..exceptions import IncorrectBackgroundError
from ..utils import get_chat, remove_kbd, show_message

logger = getLogger(__name__)


class ManagerImpl(DialogManager):
    def __init__(self, event: ChatEvent, registry: DialogRegistryProto,
                 data: Dict):
        self.disabled = False
        self._registry = registry
        self.event = event
        self.data = data
        self.show_mode: ShowMode = ShowMode.AUTO

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

    def is_preview(self) -> bool:
        return False

    def dialog(self) -> ManagedDialogAdapterProto:
        return ManagedDialogAdapter(self._dialog(), self)

    def _dialog(self) -> ManagedDialogProto:
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
        message = Message(chat=chat,
                          message_id=self.current_stack().last_message_id)
        await remove_kbd(self.event.bot, message)
        self.current_stack().last_message_id = None

    async def done(self, result: Any = None) -> None:
        await self._dialog().process_close(result, self)
        old_context = self.current_context()
        await self.mark_closed()
        context = self.current_context()
        if not context:
            await self._remove_kbd()
            return
        dialog = self._dialog()
        await dialog.process_result(old_context.start_data, result, self)
        if context.id == self.current_context().id:
            await self._dialog().show(self)

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
        if mode is StartMode.NORMAL:
            await self._start_normal(state, data)
        elif mode is StartMode.RESET_STACK:
            await self.reset_stack()
            await self._start_normal(state, data)
        elif mode is StartMode.NEW_STACK:
            await self._start_new_stack(state, data)
        else:
            raise ValueError(f"Unknown start mode: {mode}")

    async def reset_stack(self, remove_keyboard: bool = True) -> None:
        storage = self.storage()
        stack = self.current_stack()
        while not stack.empty():
            await storage.remove_context(stack.pop())
        if remove_keyboard:
            await self._remove_kbd()
        self.data[CONTEXT_KEY] = None

    async def _start_new_stack(self, state: State, data: Data = None) -> None:
        stack = Stack()
        await self.bg(stack_id=stack.id).start(state, data, StartMode.NORMAL)

    async def _start_normal(self, state: State, data: Data = None) -> None:
        stack = self.current_stack()
        old_dialog: Optional[ManagedDialogProto] = None
        if not stack.empty():
            old_dialog = self._dialog()
            if old_dialog.launch_mode is LaunchMode.EXCLUSIVE:
                raise ValueError(
                    "Cannot start dialog on top of one with launch_mode==SINGLE")

        new_dialog = self.registry.find_dialog(state)
        launch_mode = new_dialog.launch_mode
        if launch_mode in (LaunchMode.EXCLUSIVE, LaunchMode.ROOT):
            await self.reset_stack(remove_keyboard=False)
        if launch_mode is LaunchMode.SINGLE_TOP:
            if new_dialog is old_dialog:
                await self.storage().remove_context(stack.pop())

        await self.storage().save_context(self.current_context())
        context = stack.push(state, data)
        self.data[CONTEXT_KEY] = context
        await self._dialog().process_start(self, data, state)
        if context.id == self.current_context().id:
            await self._dialog().show(self)

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
        if new_message.show_mode is ShowMode.AUTO:
            new_message.show_mode = self._calc_show_mode()
        res = await show_message(self.event.bot, new_message, old_message)
        if isinstance(self.event, Message):
            stack.last_income_media_group_id = self.event.media_group_id
        self.show_mode = ShowMode.EDIT
        return res

    def _calc_show_mode(self) -> ShowMode:
        if self.show_mode is not ShowMode.AUTO:
            return self.show_mode
        if isinstance(self.event, Message):
            if self.event.media_group_id is None:
                return ShowMode.SEND
            elif self.event.media_group_id == self.current_stack().last_income_media_group_id:
                return ShowMode.EDIT
            else:
                return ShowMode.SEND
        return ShowMode.EDIT

    async def update(self, data: Dict) -> None:
        self.current_context().dialog_data.update(data)
        await self._dialog().show(self)

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
