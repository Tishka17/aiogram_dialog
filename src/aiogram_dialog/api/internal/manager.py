from typing import Dict, Protocol

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.protocols import DialogManager


class DialogManagerFactory(Protocol):
    def __call__(self, event: ChatEvent, data: Dict) -> DialogManager:
        raise NotImplementedError
