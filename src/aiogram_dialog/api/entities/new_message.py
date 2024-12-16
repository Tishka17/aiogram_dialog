from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from aiogram.enums import ContentType
from aiogram.types import (
    Chat,
    ForceReply,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    ReplyKeyboardMarkup,
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
    content_type: Optional[ContentType] = None


@dataclass
class NewMessage:
    chat: Chat
    thread_id: Optional[int] = None
    business_connection_id: Optional[str] = None
    text: Optional[str] = None
    reply_markup: Optional[MarkupVariant] = None
    parse_mode: Optional[str] = None
    show_mode: ShowMode = ShowMode.AUTO
    media: Optional[MediaAttachment] = None
    link_preview_options: Optional[LinkPreviewOptions] = None
