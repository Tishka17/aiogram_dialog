from dataclasses import dataclass
from typing import Optional, Protocol

from aiogram import Bot
from aiogram.types import Chat, InlineKeyboardMarkup, Message

from aiogram_dialog.api.entities import MediaAttachment, ShowMode


@dataclass
class NewMessage:
    chat: Chat
    text: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    parse_mode: Optional[str] = None
    show_mode: ShowMode = ShowMode.AUTO
    disable_web_page_preview: Optional[bool] = None
    media: Optional[MediaAttachment] = None


class MessageManagerProtocol(Protocol):
    async def remove_kbd(self, bot: Bot, old_message: Optional[Message]):
        raise NotImplementedError

    async def show_message(
            self, bot: Bot, new_message: NewMessage,
            old_message: Optional[Message],
    ):
        raise NotImplementedError
