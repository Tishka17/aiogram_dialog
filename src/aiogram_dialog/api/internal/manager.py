from abc import abstractmethod
from typing import Dict, Protocol, Any

from aiogram import Router

from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog.api.protocols import (
    DialogManager,
    DialogRegistryProtocol,
)


class DialogManagerFactory(Protocol):
    @abstractmethod
    def __call__(
        self,
        event: ChatEvent,
        data: Dict[str, Any],
        registry: DialogRegistryProtocol,
        router: Router,
    ) -> DialogManager:
        raise NotImplementedError
