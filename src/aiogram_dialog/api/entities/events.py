from dataclasses import dataclass
from typing import Optional, Union

from aiogram import Bot
from aiogram.types import (
    CallbackQuery,
    Chat,
    ChatJoinRequest,
    ChatMemberUpdated,
    Message,
    User,
    ErrorEvent,
)

from .update_event import DialogUpdateEvent

ChatEvent = Union[
    CallbackQuery,
    ChatJoinRequest,
    ChatMemberUpdated,
    DialogUpdateEvent,
    Message,
    ErrorEvent,
]


@dataclass
class EventContext:
    bot: Bot
    chat: Chat
    user: User
    thread_id: Optional[int]
    business_connection_id: Optional[str]


EVENT_CONTEXT_KEY = "aiogd_event_context"
