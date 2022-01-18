from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any, Protocol, Union, Type, Dict

from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (
    ContentType, Message, Chat, InlineKeyboardMarkup, ParseMode,
)

from ..context.context import Context
from ..context.events import DialogUpdateEvent, StartMode, ChatEvent, Data
from ..context.stack import Stack


class ShowMode(Enum):
    AUTO = "auto"
    EDIT = "edit"
    SEND = "send"


class LaunchMode(Enum):
    """
    `ROOT` dialogs will be always a root dialog in stack.
        Starting such dialogs will automatically reset stack.
        Example: main menu

    `EXCLUSIVE` dialogs can be only a single dialog in stack.
        Starting such dialogs will automatically reset stack.
        Starting other dialogs on top of them is forbidden
        Example: Banners

    `SINGLE_TOP` dialogs will not be repeated on top of stack.
        Starting the same dialog right on top of it will just replace it.
        Example: product page

    `STANDARD` dialogs have no limitations themselves
    """
    STANDARD = "standard"
    ROOT = "root"
    EXCLUSIVE = "exclusive"
    SINGLE_TOP = "single_top"


class MediaAttachment:
    def __init__(
            self,
            type: ContentType,
            url: Optional[str] = None,
            path: Optional[str] = None,
            file_id: Optional[str] = None,
            **kwargs,
    ):
        if not (url or path or file_id):
            raise ValueError("Neither url nor path not file_id are provided")
        self.type = type
        self.url = url
        self.path = path
        self.file_id = file_id
        self.kwargs = kwargs


@dataclass
class NewMessage:
    chat: Chat
    text: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    parse_mode: Optional[ParseMode] = None
    show_mode: ShowMode = ShowMode.AUTO
    disable_web_page_preview: Optional[bool] = None
    media: Optional[MediaAttachment] = None


class ManagedDialogAdapterProto:
    async def show(self):
        pass

    async def next(self):
        pass

    async def back(self):
        pass

    async def switch_to(self, state: State):
        pass

    def find(self, widget_id) -> Optional[Any]:
        pass


class ManagedDialogProto(Protocol):
    launch_mode: LaunchMode

    def register(self, registry: "DialogRegistryProto", dp: Dispatcher, *args,
                 **kwargs) -> None:
        pass

    def states_group_name(self) -> str:
        pass

    def states_group(self) -> Type[StatesGroup]:
        pass

    async def process_close(self, result: Any, manager: "DialogManager"):
        pass

    async def process_start(self, manager: "DialogManager", start_data: Any,
                            state: Optional[State] = None) -> None:
        pass

    async def show(self, manager: "DialogManager"):
        pass

    async def process_result(self, start_data: Data, result: Any,
                             manager: "DialogManager"):
        pass

    async def next(self, manager: "DialogManager"):
        pass

    async def back(self, manager: "DialogManager"):
        pass

    async def switch_to(self, state: State, manager: "DialogManager"):
        pass

    def find(self, widget_id) -> Optional["ManagedWidgetProto"]:
        pass


class MediaIdStorageProtocol(Protocol):
    async def get_media_id(
            self, path: Optional[str], type: ContentType,
    ) -> Optional[int]:
        raise NotImplementedError

    async def save_media_id(
            self, path: Optional[str], type: ContentType, media_id: str,
    ) -> None:
        raise NotImplementedError


class DialogRegistryProto(Protocol):
    def find_dialog(self, state: Union[State, str]) -> ManagedDialogProto:
        pass

    async def notify(self, event: DialogUpdateEvent) -> None:
        pass

    @property
    def media_id_storage(self) -> MediaIdStorageProtocol:
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
    ) -> "BaseDialogManager":
        pass


class DialogManager(BaseDialogManager):
    event: ChatEvent  # current processing event
    data: Dict  # data from middleware
    show_mode: ShowMode  # mode used to show messages

    def is_preview(self) -> bool:
        pass

    def current_context(self) -> Optional[Context]:
        pass

    def current_stack(self) -> Optional[Stack]:
        pass

    def dialog(self) -> ManagedDialogAdapterProto:
        pass

    async def close_manager(self) -> None:
        pass

    async def show(self, new_message: NewMessage) -> Message:
        pass

    async def reset_stack(self, remove_keyboard: bool = True) -> None:
        pass


class ManagedWidgetProto(Protocol):
    def managed(self, manager: DialogManager) -> Any:
        pass
