from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from aiogram.types import (
    Chat, ForceReply, InlineKeyboardMarkup, ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from aiogram_dialog.api.entities import MediaAttachment, ShowMode

MarkupVariant = Union[
    ForceReply, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove,
]


class UnknownText(Enum):
    UNKNOWN = object()


@dataclass
class OldMessage:
    chat: Chat
    message_id: int
    media_id: Optional[str]
    media_uniq_id: Optional[str]
    text: Union[str, None, UnknownText] = None
    has_reply_keyboard: bool = False
    business_connection_id: Optional[str] = None


@dataclass
class NewMessage:
    chat: Chat
    thread_id: Optional[int] = None
    business_connection_id: Optional[str] = None
    text: Optional[str] = None
    reply_markup: Optional[MarkupVariant] = None
    parse_mode: Optional[str] = None
    show_mode: ShowMode = ShowMode.AUTO
    disable_web_page_preview: Optional[bool] = None
    media: Optional[MediaAttachment] = None
