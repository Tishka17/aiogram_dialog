from typing import Union

from aiogram.types import CallbackQuery, ChatMemberUpdated, Message

from .update_event import DialogUpdateEvent

ChatEvent = Union[CallbackQuery, Message, DialogUpdateEvent, ChatMemberUpdated]
