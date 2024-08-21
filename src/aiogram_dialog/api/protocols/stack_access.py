from abc import abstractmethod
from typing import Optional, Protocol

from aiogram_dialog import ChatEvent
from aiogram_dialog.api.entities import Context, Stack


class StackAccessValidator(Protocol):
    @abstractmethod
    async def is_allowed(
            self,
            stack: Stack,
            context: Optional[Context],
            event: ChatEvent,
            data: dict,
    ) -> bool:
        """Check if current user is allowed to interactor with dialog."""
        raise NotImplementedError
