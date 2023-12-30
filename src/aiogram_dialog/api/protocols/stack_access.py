from abc import abstractmethod
from typing import Protocol

from aiogram_dialog import ChatEvent
from aiogram_dialog.api.entities import Stack


class StackAccessValidator(Protocol):
    @abstractmethod
    async def is_allowed(
            self, stack: Stack, event: ChatEvent, data: dict,
    ) -> bool:
        raise NotImplementedError
