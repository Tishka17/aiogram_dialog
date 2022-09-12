from typing import (
    Any,
    Dict,
    Protocol,
)

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from aiogram_dialog.api.protocols import DialogProtocol
from .dialog import DialogShowerProtocol
from .manager import InternalDialogManager
from .new_message import NewMessage


class WindowProtocol(Protocol):
    async def render_text(self, data: Dict,
                          manager: InternalDialogManager) -> str:
        raise NotImplementedError

    async def render_kbd(
            self, data: Dict, manager: InternalDialogManager,
    ) -> InlineKeyboardMarkup:
        raise NotImplementedError

    async def load_data(
            self,
            dialog: "DialogShowerProtocol",
            manager: InternalDialogManager,
    ) -> Dict:
        raise NotImplementedError

    async def process_message(
            self,
            m: Message,
            dialog: "DialogProtocol",
            manager: InternalDialogManager,
    ):
        raise NotImplementedError

    async def process_callback(
            self,
            c: CallbackQuery,
            dialog: "DialogProtocol",
            manager: InternalDialogManager,
    ):
        raise NotImplementedError

    async def render(
            self,
            dialog: "DialogShowerProtocol",
            manager: InternalDialogManager,
    ) -> NewMessage:
        raise NotImplementedError

    def get_state(self) -> State:
        raise NotImplementedError

    def find(self, widget_id) -> Any:
        raise NotImplementedError
