from dataclasses import dataclass
from typing import Optional

from aiogram import Bot
from aiogram.types import Message, CallbackQuery, Chat, ParseMode
from aiogram.utils.exceptions import MessageNotModified, MessageCantBeEdited, MessageToEditNotFound

from .manager.intent import (
    DialogUpdateEvent, ChatEvent
)


def get_chat(event: ChatEvent) -> Chat:
    if isinstance(event, (Message, DialogUpdateEvent)):
        return event.chat
    elif isinstance(event, CallbackQuery):
        return event.message.chat


@dataclass
class MessageParams:
    parse_mode: Optional[ParseMode] = None
    force_new: bool = False


async def show_message(bot: Bot, new_message: Message, old_message: Message, params: MessageParams):
    if not old_message or params.force_new:
        await remove_kbd(bot, old_message)
        return await send_message(bot, new_message, params)
    if new_message.text == old_message.text and new_message.reply_markup == old_message.reply_markup:
        return old_message
    try:
        return await bot.edit_message_text(
            message_id=old_message.message_id, chat_id=old_message.chat.id,
            text=new_message.text, reply_markup=new_message.reply_markup,
            parse_mode=params.parse_mode,
        )
    except MessageNotModified:
        return old_message
    except (MessageCantBeEdited, MessageToEditNotFound):
        return await send_message(bot, new_message, params)


async def remove_kbd(bot: Bot, old_message: Optional[Message]):
    if old_message:
        try:
            await bot.edit_message_reply_markup(
                message_id=old_message.message_id, chat_id=old_message.chat.id
            )
        except (MessageNotModified, MessageCantBeEdited, MessageToEditNotFound):
            pass  # nothing to remove


async def send_message(bot: Bot, new_message: Message, params: MessageParams):
    return await bot.send_message(
        chat_id=new_message.chat.id,
        text=new_message.text,
        reply_markup=new_message.reply_markup,
        parse_mode=params.parse_mode,
    )
