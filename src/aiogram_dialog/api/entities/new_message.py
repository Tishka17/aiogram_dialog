from dataclasses import dataclass
from typing import Optional

from aiogram.types import Chat, InlineKeyboardMarkup

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
