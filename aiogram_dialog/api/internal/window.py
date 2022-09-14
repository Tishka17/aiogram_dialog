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
    async def render_text(self, data: Dict,
                          manager: DialogManager) -> str:
        raise NotImplementedError

    async def render_kbd(
            self, data: Dict, manager: DialogManager,
    ) -> InlineKeyboardMarkup:
        raise NotImplementedError

    async def load_data(
            self,
            dialog: "DialogProtocol",
            manager: DialogManager,
    ) -> Dict:
        raise NotImplementedError

    async def process_message(
            self,
            message: Message,
            dialog: "DialogProtocol",
            manager: DialogManager,
    ):
        raise NotImplementedError

    async def process_callback(
            self,
            callback: CallbackQuery,
            dialog: "DialogProtocol",
            manager: DialogManager,
    ):
        raise NotImplementedError

    async def render(
            self,
            dialog: "DialogProtocol",
            manager: DialogManager,
    ) -> NewMessage:
        raise NotImplementedError

    def get_state(self) -> State:
        raise NotImplementedError

    def find(self, widget_id) -> Any:
        raise NotImplementedError
