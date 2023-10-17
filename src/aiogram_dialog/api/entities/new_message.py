from dataclasses import dataclass
from typing import Optional, Union

from aiogram.types import (
    Chat, InlineKeyboardMarkup, ReplyKeyboardMarkup,
    ReplyKeyboardRemove, ForceReply,
)

from aiogram_dialog.api.entities import MediaAttachment, ShowMode

MarkupVariant = Union[
    InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply,
]


@dataclass
class NewMessage:
    chat: Chat
    text: Optional[str] = None
    reply_markup: Optional[MarkupVariant] = None
    parse_mode: Optional[str] = None
    show_mode: ShowMode = ShowMode.AUTO
    disable_web_page_preview: Optional[bool] = None
    media: Optional[MediaAttachment] = None
