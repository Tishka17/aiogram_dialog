from abc import abstractmethod
from typing import Optional, Protocol

from aiogram import Bot
from aiogram.types import CallbackQuery, Message

from aiogram_dialog.api.entities import NewMessage
from aiogram_dialog.api.exceptions import DialogsError


class MessageNotModified(DialogsError):
    pass


class MessageManagerProtocol(Protocol):
    @abstractmethod
    async def remove_kbd(
            self, bot: Bot, old_message: Optional[Message],
    ) -> Optional[Message]:
        raise NotImplementedError

    @abstractmethod
    async def show_message(
            self, bot: Bot, new_message: NewMessage,
            old_message: Optional[Message],
    ) -> Message:
        raise NotImplementedError

    @abstractmethod
    async def answer_callback(
            self, bot: Bot, callback_query: CallbackQuery,
    ) -> None:
        raise NotImplementedError
