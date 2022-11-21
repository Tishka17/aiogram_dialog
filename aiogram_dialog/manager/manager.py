from datetime import datetime
from logging import getLogger
from typing import Any, Dict, Optional

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Chat, Document, Message, User

from aiogram_dialog.api.entities import (
    ChatEvent, Context, Data, DEFAULT_STACK_ID, LaunchMode, NewMessage,
    ShowMode, Stack, StartMode,
)
from aiogram_dialog.api.exceptions import IncorrectBackgroundError
from aiogram_dialog.api.internal import (
    CONTEXT_KEY, STACK_KEY, STORAGE_KEY,
)
from aiogram_dialog.api.internal import (
    FakeChat, FakeUser,
)
from aiogram_dialog.api.protocols import (
    BaseDialogManager, DialogManager, DialogProtocol, DialogRegistryProtocol,
    MediaIdStorageProtocol, MessageManagerProtocol,
)
from aiogram_dialog.context.storage import StorageProxy
from aiogram_dialog.utils import get_media_id
from .bg_manager import BgManager

logger = getLogger(__name__)


class ManagerImpl(DialogManager):

    def __init__(
            self, event: ChatEvent,
            message_manager: MessageManagerProtocol,
            media_id_storage: MediaIdStorageProtocol,
            registry: DialogRegistryProtocol,
            data: Dict,
    ):
        self.disabled = False
        self.message_manager = message_manager
        self.media_id_storage = media_id_storage
        self._event = event
        self._data = data
        self._show_mode: ShowMode = ShowMode.AUTO
        self._registry = registry

    @property
    def show_mode(self) -> ShowMode:
        """Get current show mode, used for next show action."""
        return self._show_mode

    @show_mode.setter
    def show_mode(self, show_mode: ShowMode) -> None:
        """Set current show mode, used for next show action."""
        self._show_mode = show_mode

    @property
    def event(self) -> ChatEvent:
        return self._event

    @property
    def middleware_data(self) -> Dict:
        """Middleware data."""
        return self._data

    @property
    def dialog_data(self) -> Dict:
        """Dialog data for current context."""
        return self.current_context().dialog_data

    @property
    def start_data(self) -> Dict:
        """Start data for current context."""
        return self.current_context().start_data

    def check_disabled(self):
        if self.disabled:
            raise IncorrectBackgroundError(
                "Detected background access to dialog manager. "
                "Please use background manager available via `manager.bg()` "
                "method to access methods from background tasks",
            )

    async def load_data(self) -> Dict:
        context = self.current_context()
        return {
            "dialog_data": context.dialog_data,
            "start_data": context.start_data,
            "middleware_data": self._data,
            "event": self.event,
        }

    def is_preview(self) -> bool:
        return False

    def dialog(self) -> DialogProtocol:
        self.check_disabled()
        current = self.current_context()
        if not current:
            raise RuntimeError
        return self._registry.find_dialog(current.state)

    def current_context(self) -> Optional[Context]:
        self.check_disabled()
        return self._data[CONTEXT_KEY]

    def current_stack(self) -> Optional[Stack]:
        self.check_disabled()
        return self._data[STACK_KEY]

    def storage(self) -> StorageProxy:
        return self._data[STORAGE_KEY]

    async def _remove_kbd(self) -> None:
        if self.current_stack().last_message_id is None:
            return
        chat = self._data["event_chat"]
        bot = self._data["bot"]
        message = Message(
            chat=chat,
            message_id=self.current_stack().last_message_id,
            date=datetime.now(),
        )
        await self.message_manager.remove_kbd(
            bot,
            message,
        )
        self.current_stack().last_message_id = None

    async def _process_last_dialog_result(
            self,
            start_data: Data,
            result: Any,
    ) -> None:
        """Process closing last dialog in stack."""
        await self._remove_kbd()

    async def done(self, result: Any = None) -> None:
        self.check_disabled()
        await self.dialog().process_close(result, self)
        old_context = self.current_context()
        await self.mark_closed()
        context = self.current_context()
        if not context:
            await self._process_last_dialog_result(
                old_context.start_data,
                result,
            )
            return
        dialog = self.dialog()
        await dialog.process_result(old_context.start_data, result, self)
        new_context = self.current_context()
        if new_context and context.id == new_context.id:
            await self.show()

    async def mark_closed(self) -> None:
        self.check_disabled()
        storage = self.storage()
        stack = self.current_stack()
        await storage.remove_context(stack.pop())
        if stack.empty():
            self._data[CONTEXT_KEY] = None
        else:
            intent_id = stack.last_intent_id()
            self._data[CONTEXT_KEY] = await storage.load_context(intent_id)
        await storage.save_stack(stack)

    async def start(
            self,
            state: State,
            data: Data = None,
            mode: StartMode = StartMode.NORMAL,
            show_mode: ShowMode = ShowMode.AUTO,
    ) -> None:
        self.check_disabled()
        self.show_mode = show_mode
        if mode is StartMode.NORMAL:
            await self._start_normal(state, data)
        elif mode is StartMode.RESET_STACK:
            await self.reset_stack(remove_keyboard=False)
            await self._start_normal(state, data)
        elif mode is StartMode.NEW_STACK:
            await self._start_new_stack(state, data)
        else:
            raise ValueError(f"Unknown start mode: {mode}")

    async def reset_stack(self, remove_keyboard: bool = True) -> None:
        self.check_disabled()
        storage = self.storage()
        stack = self.current_stack()
        while not stack.empty():
            await storage.remove_context(stack.pop())
        await storage.save_stack(stack)
        if remove_keyboard:
            await self._remove_kbd()
        self._data[CONTEXT_KEY] = None

    async def _start_new_stack(self, state: State, data: Data = None) -> None:
        stack = Stack()
        await self.bg(stack_id=stack.id).start(state, data, StartMode.NORMAL)

    async def _start_normal(self, state: State, data: Data = None) -> None:
        stack = self.current_stack()
        old_dialog: Optional[DialogProtocol] = None
        if not stack.empty():
            old_dialog = self.dialog()
            if old_dialog.launch_mode is LaunchMode.EXCLUSIVE:
                raise ValueError(
                    "Cannot start dialog on top "
                    "of one with launch_mode==SINGLE",
                )

        new_dialog = self._registry.find_dialog(state)
        launch_mode = new_dialog.launch_mode
        if launch_mode in (LaunchMode.EXCLUSIVE, LaunchMode.ROOT):
            await self.reset_stack(remove_keyboard=False)
        if launch_mode is LaunchMode.SINGLE_TOP:
            if new_dialog is old_dialog:
                await self.storage().remove_context(stack.pop())

        await self.storage().save_context(self.current_context())
        context = stack.push(state, data)
        self._data[CONTEXT_KEY] = context
        await self.dialog().process_start(self, data, state)
        if context.id == self.current_context().id:
            await self.show()

    async def next(self) -> None:
        context = self.current_context()
        if not context:
            raise ValueError("No intent")
        states = self.dialog().states()
        current_index = states.index(context.state)
        new_state = states[current_index + 1]
        await self.switch_to(new_state)

    async def back(self) -> None:
        context = self.current_context()
        if not context:
            raise ValueError("No intent")
        states = self.dialog().states()
        current_index = states.index(context.state)
        new_state = states[current_index - 1]
        await self.switch_to(new_state)

    async def switch_to(self, state: State) -> None:
        self.check_disabled()
        context = self.current_context()
        if context.state.group != state.group:
            raise ValueError(
                f"Cannot switch to another state group. "
                f"Current state: {context.state}, asked for {state}",
            )
        context.state = state

    async def show(self) -> Message:
        stack = self.current_stack()
        bot = self._data["bot"]
        old_message = self._get_last_message()
        new_message = await self.dialog().render(self)
        if new_message.show_mode is ShowMode.AUTO:
            new_message.show_mode = self._calc_show_mode()
        await self._fix_cached_media_id(new_message)

        sent_message = await self.message_manager.show_message(
            bot, new_message, old_message,
        )

        self._save_last_message(sent_message)
        self.show_mode = ShowMode.EDIT
        if new_message.media:
            await self.media_id_storage.save_media_id(
                path=new_message.media.path,
                url=new_message.media.url,
                type=new_message.media.type,
                media_id=get_media_id(sent_message),
            )
        if isinstance(self.event, Message):
            stack.last_income_media_group_id = self.event.media_group_id
        return sent_message

    async def _fix_cached_media_id(self, new_message: NewMessage):
        if not new_message.media or new_message.media.file_id:
            return
        new_message.media.file_id = await self.media_id_storage.get_media_id(
            path=new_message.media.path,
            url=new_message.media.url,
            type=new_message.media.type,
        )

    def _get_last_message(self) -> Optional[Message]:
        stack = self.current_stack()
        chat = self._data["event_chat"]
        if (
                isinstance(self.event, CallbackQuery) and
                self.event.message and
                stack.last_message_id == self.event.message.message_id
        ):
            return self.event.message
        if not stack or not stack.last_message_id:
            return None
        if stack.last_media_id:
            # we create document because
            # * there is no method to set content type explicitly
            # * we don't really care fo exact content type
            document = Document(
                file_id=stack.last_media_id,
                file_unique_id=stack.last_media_unique_id,
            )
            text = None
        else:
            document = None
            # we set some non empty-text which is not equal to anything
            text = "𝔞𝔦𝔬𝔤𝔯𝔞𝔪 𝔡𝔦𝔞𝔩𝔬𝔤 𝔲𝔫𝔦𝔮𝔲𝔢 𝔱𝔢𝔵𝔱"
        return Message(
            message_id=stack.last_message_id,
            document=document,
            text=text,
            chat=chat,
            date=datetime.now(),
        )

    def _save_last_message(self, message: Message):
        stack = self.current_stack()
        stack.last_message_id = message.message_id
        media_id = get_media_id(message)
        if media_id:
            stack.last_media_id = media_id.file_id
            stack.last_media_unique_id = media_id.file_unique_id
        else:
            stack.last_media_id = None
            stack.last_media_unique_id = None

    def _calc_show_mode(self) -> ShowMode:
        if self.show_mode is not ShowMode.AUTO:
            return self.show_mode
        if self.current_stack().id != DEFAULT_STACK_ID:
            return ShowMode.EDIT
        if isinstance(self.event, Message):
            if self.event.media_group_id is None:
                return ShowMode.SEND
            elif self.event.media_group_id == \
                    self.current_stack().last_income_media_group_id:
                return ShowMode.EDIT
            else:
                return ShowMode.SEND
        return ShowMode.EDIT

    async def update(self, data: Dict) -> None:
        self.current_context().dialog_data.update(data)
        await self.show()

    def find(self, widget_id) -> Optional[Any]:
        widget = self.dialog().find(widget_id)
        if not widget:
            return None
        return widget.managed(self)

    def is_same_chat(self, user: User, chat: Chat) -> bool:
        if "event_chat" not in self._data:
            return False

        current_chat = self._data["event_chat"]
        current_user = self.event.from_user
        return user.id == current_user.id and chat.id == current_chat.id

    def _get_fake_user(self, user_id: Optional[int] = None) -> User:
        """Get User if we have info about him or FakeUser instead."""
        current_user = self.event.from_user
        if user_id in (None, current_user.id):
            return current_user
        return FakeUser(id=user_id, is_bot=False, first_name="")

    def _get_fake_chat(self, chat_id: Optional[int] = None) -> Chat:
        """Get Chat if we have info about him or FakeChat instead."""
        if "event_chat" in self._data:
            current_chat = self._data["event_chat"]
            if chat_id in (None, current_chat.id):
                return current_chat
        elif chat_id is None:
            raise ValueError(
                "Explicit `chat_id` is required "
                "for events without current chat",
            )
        return FakeChat(id=chat_id, type="")

    def bg(
            self,
            user_id: Optional[int] = None,
            chat_id: Optional[int] = None,
            stack_id: Optional[str] = None,
            load: bool = False,
    ) -> "BaseDialogManager":
        user = self._get_fake_user(user_id)
        chat = self._get_fake_chat(chat_id)
        intent_id = None
        if stack_id is None:
            if self.is_same_chat(user, chat):
                stack_id = self.current_stack().id
                if self.current_context():
                    intent_id = self.current_context().id
            else:
                stack_id = DEFAULT_STACK_ID

        return BgManager(
            user=user,
            chat=chat,
            bot=self._data["bot"],
            registry=self._registry,
            intent_id=intent_id,
            stack_id=stack_id,
            load=load,
        )

    async def close_manager(self) -> None:
        self.check_disabled()
        self.disabled = True
        del self.media_id_storage
        del self.message_manager
        del self._event
        del self._data
