from typing import Dict, Protocol

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.protocols import (
    DialogManager, MediaIdStorageProtocol, MessageManagerProtocol,
)


class DialogManagerFactory(Protocol):
    def __call__(
            self,
            event: ChatEvent,
            message_manager: MessageManagerProtocol,
            media_id_storage: MediaIdStorageProtocol,
            data: Dict,
    ) -> DialogManager:
        raise NotImplementedError
