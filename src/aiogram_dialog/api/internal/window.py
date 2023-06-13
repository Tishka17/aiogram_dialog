from abc import abstractmethod
from typing import (
    Any,
    Dict,
    Protocol,
)

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from aiogram_dialog.api.entities import NewMessage
from aiogram_dialog.api.protocols import DialogProtocol
from .manager import DialogManager


class WindowProtocol(Protocol):
    @abstractmethod
    async def render_text(self, data: Dict,
                          manager: DialogManager) -> str:
        raise NotImplementedError

    @abstractmethod
    async def render_kbd(
            self, data: Dict, manager: DialogManager,
    ) -> InlineKeyboardMarkup:
        raise NotImplementedError

    @abstractmethod
    async def load_data(
            self,
            dialog: "DialogProtocol",
            manager: DialogManager,
    ) -> Dict:
        raise NotImplementedError

    @abstractmethod
    async def process_message(
            self,
            message: Message,
            dialog: "DialogProtocol",
            manager: DialogManager,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def process_callback(
            self,
            callback: CallbackQuery,
            dialog: "DialogProtocol",
            manager: DialogManager,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def render(
            self,
            dialog: "DialogProtocol",
            manager: DialogManager,
    ) -> NewMessage:
        raise NotImplementedError

    @abstractmethod
    def get_state(self) -> State:
        raise NotImplementedError

    @abstractmethod
    def find(self, widget_id) -> Any:
        raise NotImplementedError
