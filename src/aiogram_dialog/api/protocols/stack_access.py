from abc import abstractmethod
from typing import Protocol

from aiogram.types import Chat, User

from aiogram_dialog.api.entities import Stack


class StackAccessValidator(Protocol):
    @abstractmethod
    async def is_allowed(
            self, stack: Stack, user: User, chat: Chat,
    ) -> bool:
        raise NotImplementedError
