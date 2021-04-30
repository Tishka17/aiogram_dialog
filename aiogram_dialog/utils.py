
from aiogram import Bot
from aiogram.dispatcher.filters.state import State
from aiogram.types import Message, CallbackQuery, Chat, User

from .manager.intent import (
    DialogUpdateEvent, ChatEvent
)


def get_chat(event: ChatEvent) -> Chat:
    if isinstance(event, (Message, DialogUpdateEvent)):
        return event.chat
    elif isinstance(event, CallbackQuery):
        return event.message.chat
