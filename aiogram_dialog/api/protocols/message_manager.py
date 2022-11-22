from typing import Optional, Protocol

from aiogram import Bot
from aiogram.types import CallbackQuery, Message

from aiogram_dialog.api.entities import NewMessage


class MessageManagerProtocol(Protocol):
    async def remove_kbd(self, bot: Bot, old_message: Optional[Message]):
        raise NotImplementedError

    async def show_message(
            self, bot: Bot, new_message: NewMessage,
            old_message: Optional[Message],
    ):
        raise NotImplementedError

    async def answer_callback(
            self, bot: Bot, callback_query: CallbackQuery,
    ) -> None:
        raise NotImplementedError
