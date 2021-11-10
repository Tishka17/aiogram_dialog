from dataclasses import dataclass
from typing import Optional, Tuple, Union

from aiogram import Bot
from aiogram.types import Message, CallbackQuery, Chat, ParseMode, \
    InlineKeyboardMarkup, ChatMemberUpdated, InputFile, ContentType, InputMedia
from aiogram.utils.exceptions import (
    MessageNotModified, MessageCantBeEdited, MessageToEditNotFound,
    MessageToDeleteNotFound, MessageCantBeDeleted,
)

from .context.events import (
    DialogUpdateEvent, ChatEvent
)
from .context.media_storage import MediaIdStorage, Media

CB_SEP = "\x1D"

send_methods = {
    ContentType.ANIMATION: "send_animation",
    ContentType.AUDIO: "send_audio",
    ContentType.DOCUMENT: "send_document",
    ContentType.PHOTO: "send_photo",
    ContentType.VIDEO: "send_video",
}
media_storage = MediaIdStorage()


def get_chat(event: ChatEvent) -> Chat:
    if isinstance(event, (Message, DialogUpdateEvent, ChatMemberUpdated)):
        return event.chat
    elif isinstance(event, CallbackQuery):
        if not event.message:
            return Chat(id=event.from_user.id)
        return event.message.chat


def get_media_id(message: Message) -> Optional[str]:
    if message.audio:
        return message.audio.file_id
    if message.animation:
        return message.animation.file_id
    if message.document:
        return message.document.file_id
    if message.photo:
        return message.photo[-1].file_id
    if message.video:
        return message.video.file_id
    return None


@dataclass
class NewMessage:
    chat: Chat
    text: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    parse_mode: Optional[ParseMode] = None
    force_new: bool = False
    disable_web_page_preview: Optional[bool] = None
    media: Optional[Media] = None


def intent_callback_data(intent_id: str, callback_data: Optional[str]) -> Optional[str]:
    if callback_data is None:
        return None
    return intent_id + CB_SEP + callback_data


def add_indent_id(message: NewMessage, intent_id: str):
    if not message.reply_markup:
        return
    for row in message.reply_markup.inline_keyboard:
        for button in row:
            button.callback_data = intent_callback_data(
                intent_id, button.callback_data
            )


def remove_indent_id(callback_data: str) -> Tuple[str, str]:
    if CB_SEP in callback_data:
        intent_id, new_data = callback_data.split(CB_SEP, maxsplit=1)
        return intent_id, new_data
    return "", callback_data


async def show_message(bot: Bot, new_message: NewMessage,
                       old_message: Message):
    if not old_message or new_message.force_new:
        await remove_kbd(bot, old_message)
        return await send_message(bot, new_message)
    if (
            new_message.text == old_message.text and
            new_message.reply_markup == old_message.reply_markup and
            bool(new_message.media) == (old_message.content_type == ContentType.TEXT)
    ):
        return old_message
    if bool(new_message.media) != (old_message.content_type != ContentType.TEXT):
        try:
            await bot.delete_message(chat_id=old_message.chat.id, message_id=old_message.message_id)
        except (MessageToDeleteNotFound, MessageCantBeDeleted):
            await remove_kbd(bot, old_message)
        return await send_message(bot, new_message)

    try:
        if new_message.media:
            media = InputMedia(
                caption=new_message.text,
                reply_markup=new_message.reply_markup,
                parse_mode=new_message.parse_mode,
                disable_web_page_preview=new_message.disable_web_page_preview,
                media=await media_storage.get_media_source(new_message.media),
                **new_message.media.kwargs,
            )
            return await bot.edit_message_media(
                message_id=old_message.message_id,
                chat_id=old_message.chat.id,
                media=media,
            )
        else:
            return await bot.edit_message_text(
                message_id=old_message.message_id,
                chat_id=old_message.chat.id,
                text=new_message.text,
                reply_markup=new_message.reply_markup,
                parse_mode=new_message.parse_mode,
                disable_web_page_preview=new_message.disable_web_page_preview,
            )
    except MessageNotModified:
        return old_message
    except (MessageCantBeEdited, MessageToEditNotFound):
        return await send_message(bot, new_message)


async def remove_kbd(bot: Bot, old_message: Optional[Message]):
    if old_message:
        try:
            await bot.edit_message_reply_markup(
                message_id=old_message.message_id, chat_id=old_message.chat.id
            )
        except (
                MessageNotModified, MessageCantBeEdited,
                MessageToEditNotFound):
            pass  # nothing to remove


async def send_message(bot: Bot, new_message: NewMessage):
    kwargs = {
        "reply_markup": new_message.reply_markup,
        "parse_mode": new_message.parse_mode,
    }
    if not new_message.media:
        return await bot.send_message(
            new_message.chat.id,
            text=new_message.text,
            disable_web_page_preview=new_message.disable_web_page_preview,
            **kwargs,
        )
    else:
        method = getattr(bot, send_methods[new_message.media.type])
        return await method(
            new_message.chat.id,
            await media_storage.get_media_source(new_message.media),
            caption=new_message.text,
            **kwargs,
            **new_message.media.kwargs,
        )