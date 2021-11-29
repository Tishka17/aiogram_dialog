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


class EditMode(Enum):
    EDIT_ON_MESSAGE = "edit_on_message"
    EDIT = "edit"
    SEND = "send"


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
    force_new: bool = False
    disable_web_page_preview: Optional[bool] = None
    media: Optional[MediaAttachment] = None


class ManagedDialogProto(Protocol):
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

    async def show(self, manager: "DialogManager", preview: bool = False):
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

    def find(self, widget_id) -> Optional[Any]:
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

    def current_context(self) -> Optional[Context]:
        pass

    def current_stack(self) -> Optional[Stack]:
        pass

    def dialog(self) -> ManagedDialogProto:
        pass

    async def close_manager(self) -> None:
        pass

    async def show(self, new_message: NewMessage) -> Message:
        pass
