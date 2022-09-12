from typing import Any, Dict, Protocol

from aiogram.types import Message

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.protocols import ActiveDialogManager
from .new_message import NewMessage


class ActiveStateManager(Protocol):
    def is_preview(self) -> bool:
        raise NotImplementedError

    async def show(self, new_message: NewMessage) -> Message:
        raise NotImplementedError

    async def load_data(self) -> Dict:
        raise NotImplementedError

    async def close_manager(self) -> None:
        raise NotImplementedError


class InternalDialogManager(ActiveDialogManager, ActiveStateManager, Protocol):
    pass


class DialogManagerFactory(Protocol):
    def __call__(
            self,
            event: ChatEvent,
            message_manager: Any,  # TODO
            data: Dict,
    ) -> InternalDialogManager:
        raise NotImplementedError
