from abc import abstractmethod
from typing import Protocol, Optional

from aiogram_dialog import ChatEvent
from aiogram_dialog.api.entities import Stack, Context


class StackAccessValidator(Protocol):
    @abstractmethod
    async def is_allowed(
            self,
            stack: Stack,
            context: Optional[Context],
            event: ChatEvent,
            data: dict,
    ) -> bool:
        raise NotImplementedError
