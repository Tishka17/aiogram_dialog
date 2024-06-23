from dataclasses import dataclass
from typing import Union, Optional

from aiogram import Bot
from aiogram.types import (
    CallbackQuery, ChatJoinRequest, ChatMemberUpdated, Message, Chat, User,
)

from .update_event import DialogUpdateEvent

ChatEvent = Union[
    CallbackQuery, Message, DialogUpdateEvent,
    ChatMemberUpdated, ChatJoinRequest,
]


@dataclass
class EventContext:
    bot: Bot
    chat: Chat
    user: User
    thread_id: Optional[int]
    business_connection_id: Optional[str]


EVENT_CONTEXT_KEY = "aiogd_event_context"