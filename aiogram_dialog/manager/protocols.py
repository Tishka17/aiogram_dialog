from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, Type, Union

from aiogram import Bot, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Chat, InlineKeyboardMarkup, Message

from aiogram_dialog.api.entities import (
    ChatEvent, Context, Data, DialogUpdate, LaunchMode,
    MediaAttachment, ShowMode, Stack,
    StartMode,
)
from aiogram_dialog.api.protocols import (
    ManagedDialogProtocol, MediaIdStorageProtocol,
)


class ManagedDialogProto(Protocol):
    launch_mode: LaunchMode

    def register(
            self, registry: "DialogRegistryProto", router: Router, *args,
            **kwargs,
    ) -> None:
        pass

    def states_group_name(self) -> str:
        pass

    def states_group(self) -> Type[StatesGroup]:
        pass

    async def process_close(self, result: Any, manager: "DialogManager"):
        pass

    async def process_start(
            self,
            manager: "DialogManager",
            start_data: Any,
            state: Optional[State] = None,
    ) -> None:
        pass

    async def show(self, manager: "DialogManager"):
        pass

    async def process_result(
            self, start_data: Data, result: Any, manager: "DialogManager",
    ):
        pass

    async def next(self, manager: "DialogManager"):
        pass

    async def back(self, manager: "DialogManager"):
        pass

    async def switch_to(self, state: State, manager: "DialogManager"):
        pass

    def find(self, widget_id) -> Optional["ManagedWidgetProto"]:
        pass


@dataclass
class NewMessage:
    chat: Chat
    text: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    parse_mode: Optional[str] = None
    show_mode: ShowMode = ShowMode.AUTO
    disable_web_page_preview: Optional[bool] = None
    media: Optional[MediaAttachment] = None


class MessageManagerProtocol(Protocol):
    async def remove_kbd(self, bot: Bot, old_message: Optional[Message]):
        raise NotImplementedError

    async def show_message(
            self, bot: Bot, new_message: NewMessage,
            old_message: Optional[Message],
    ):
        raise NotImplementedError


class DialogRegistryProto(Protocol):
    def find_dialog(self, state: Union[State, str]) -> ManagedDialogProto:
        pass

    async def notify(self, bot: Bot, update: DialogUpdate) -> None:
        pass

    @property
    def media_id_storage(self) -> MediaIdStorageProtocol:
        raise NotImplementedError

    @property
    def message_manager(self) -> MessageManagerProtocol:
        raise NotImplementedError


class BaseDialogManager(Protocol):
    event: ChatEvent

    @property
    def registry(self) -> DialogRegistryProto:
        raise NotImplementedError

    async def done(self, result: Any = None) -> None:
        pass

    async def mark_closed(self) -> None:
        pass

    async def start(
            self,
            state: State,
            data: Data = None,
            mode: StartMode = StartMode.NORMAL,
            show_mode: ShowMode = ShowMode.AUTO,
    ) -> None:
        pass

    async def switch_to(self, state: State) -> None:
        pass

    async def update(self, data: Dict) -> None:
        pass

    def bg(
            self,
            user_id: Optional[int] = None,
            chat_id: Optional[int] = None,
            stack_id: Optional[str] = None,
            load: bool = False,  # load chat and user
    ) -> "BaseDialogManager":
        pass


class DialogManager(BaseDialogManager, Protocol):
    event: ChatEvent  # current processing event
    data: Dict  # data from middleware
    show_mode: ShowMode  # mode used to show messages

    def is_preview(self) -> bool:
        raise NotImplementedError

    def current_context(self) -> Optional[Context]:
        raise NotImplementedError

    def current_stack(self) -> Optional[Stack]:
        raise NotImplementedError

    def dialog(self) -> ManagedDialogProtocol:
        raise NotImplementedError

    async def close_manager(self) -> None:
        raise NotImplementedError

    async def show(self, new_message: NewMessage) -> Message:
        raise NotImplementedError

    async def reset_stack(self, remove_keyboard: bool = True) -> None:
        raise NotImplementedError

    async def load_data(self) -> Dict:
        raise NotImplementedError


class DialogManagerFactory(Protocol):
    def __call__(
            self,
            event: ChatEvent,
            registry: DialogRegistryProto,
            data: Dict,
    ) -> DialogManager:
        raise NotImplementedError


class ManagedWidgetProto(Protocol):
    def managed(self, manager: DialogManager) -> Any:
        pass
