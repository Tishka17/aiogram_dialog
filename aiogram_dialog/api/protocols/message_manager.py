from typing import Optional, Protocol

from aiogram import Bot
from aiogram.types import Message

from aiogram_dialog.api.entities import NewMessage


class MessageManagerProtocol(Protocol):
    # Shao-mod
    async def new_text(self, bot: Bot, new_text: str, old_message: Optional[Message]):
        raise NotImplementedError

    async def remove_kbd(self, bot: Bot, old_message: Optional[Message]):
        raise NotImplementedError

    async def show_message(
            self, bot: Bot, new_message: NewMessage,
            old_message: Optional[Message],
    ):
        raise NotImplementedError
