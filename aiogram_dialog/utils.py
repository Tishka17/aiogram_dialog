from logging import getLogger
from typing import Optional, Tuple, Union, IO

from aiogram import Bot
from aiogram.types import (
    Message, CallbackQuery, Chat, ChatMemberUpdated, ContentType, InputMedia,
)
from aiogram.utils.exceptions import (
    MessageNotModified, MessageCantBeEdited, MessageToEditNotFound,
    MessageToDeleteNotFound, MessageCantBeDeleted,
)

from .context.events import (
    DialogUpdateEvent, ChatEvent
)
from .manager.protocols import MediaAttachment, NewMessage, ShowMode

logger = getLogger(__name__)

CB_SEP = "\x1D"

send_methods = {
    ContentType.ANIMATION: "send_animation",
    ContentType.AUDIO: "send_audio",
    ContentType.DOCUMENT: "send_document",
    ContentType.PHOTO: "send_photo",
    ContentType.VIDEO: "send_video",
}


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


async def get_media_source(media: MediaAttachment) -> Union[IO, str]:
    if media.file_id:
        return media.file_id
    if media.url:
        return media.url
    else:
        return open(media.path, "rb")


def intent_callback_data(intent_id: str,
                         callback_data: Optional[str]) -> Optional[str]:
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
                       old_message: Optional[Message]):
    if not old_message or new_message.show_mode is ShowMode.SEND:
        logger.debug("Send new message, because: mode=%s, has old_message=%s",
                     new_message.show_mode, bool(old_message))
        await remove_kbd(bot, old_message)
        return await send_message(bot, new_message)

    had_media = old_message.content_type != ContentType.TEXT
    need_media = bool(new_message.media)

    if (
            new_message.text == old_message.text and
            new_message.reply_markup == old_message.reply_markup and
            had_media == need_media and
            (
                    not need_media or
                    new_message.media.file_id == get_media_id(old_message)
            )
    ):
        # nothing changed: text, keyboard or media
        return old_message

    if had_media != need_media:
        # we cannot edit message if media appeared or removed
        try:
            await bot.delete_message(chat_id=old_message.chat.id,
                                     message_id=old_message.message_id)
        except (MessageToDeleteNotFound, MessageCantBeDeleted):
            await remove_kbd(bot, old_message)
        return await send_message(bot, new_message)

    try:
        return await edit_message(bot, new_message, old_message)
    except MessageNotModified:
        return old_message
    except (MessageCantBeEdited, MessageToEditNotFound):
        return await send_message(bot, new_message)


async def remove_kbd(bot: Bot, old_message: Optional[Message]):
    if old_message:
        logger.debug("remove_kbd in %s", old_message.chat)
        try:
            await bot.edit_message_reply_markup(
                message_id=old_message.message_id,
                chat_id=old_message.chat.id,
            )
        except (MessageNotModified, MessageCantBeEdited,
                MessageToEditNotFound):
            pass  # nothing to remove


# Edit
async def edit_message(bot: Bot, new_message: NewMessage,
                       old_message: Message):
    if new_message.media:
        if new_message.media.file_id == get_media_id(old_message):
            return await edit_caption(bot, new_message, old_message)
        return await edit_media(bot, new_message, old_message)
    else:
        return await edit_text(bot, new_message, old_message)


async def edit_caption(bot: Bot, new_message: NewMessage,
                       old_message: Message):
    logger.debug("edit_caption to %s", new_message.chat)
    return await bot.edit_message_caption(
        message_id=old_message.message_id,
        chat_id=old_message.chat.id,
        caption=new_message.text,
        reply_markup=new_message.reply_markup,
        parse_mode=new_message.parse_mode,
    )


async def edit_text(bot: Bot, new_message: NewMessage,
                    old_message: Message):
    logger.debug("edit_text to %s", new_message.chat)
    return await bot.edit_message_text(
        message_id=old_message.message_id,
        chat_id=old_message.chat.id,
        text=new_message.text,
        reply_markup=new_message.reply_markup,
        parse_mode=new_message.parse_mode,
        disable_web_page_preview=new_message.disable_web_page_preview,
    )


async def edit_media(bot: Bot, new_message: NewMessage,
                     old_message: Message):
    logger.debug("edit_media to %s, media_id: %s",
                 new_message.chat, new_message.media.file_id)
    media = InputMedia(
        caption=new_message.text,
        reply_markup=new_message.reply_markup,
        parse_mode=new_message.parse_mode,
        disable_web_page_preview=new_message.disable_web_page_preview,
        media=await get_media_source(new_message.media),
        **new_message.media.kwargs,
    )
    return await bot.edit_message_media(
        message_id=old_message.message_id,
        chat_id=old_message.chat.id,
        media=media,
    )


# Send
async def send_message(bot: Bot, new_message: NewMessage):
    if new_message.media:
        return await send_media(bot, new_message)
    else:
        return await send_text(bot, new_message)


async def send_text(bot: Bot, new_message: NewMessage):
    logger.debug("send_text to %s", new_message.chat)
    return await bot.send_message(
        new_message.chat.id,
        text=new_message.text,
        disable_web_page_preview=new_message.disable_web_page_preview,
        reply_markup=new_message.reply_markup,
        parse_mode=new_message.parse_mode,
    )


async def send_media(bot: Bot, new_message: NewMessage):
    logger.debug("send_media to %s, media_id: %s",
                 new_message.chat, new_message.media.file_id)
    method = getattr(bot, send_methods[new_message.media.type], None)
    if not method:
        raise ValueError(
            f"ContentType {new_message.media.type} is not supported")
    return await method(
        new_message.chat.id,
        await get_media_source(new_message.media),
        caption=new_message.text,
        reply_markup=new_message.reply_markup,
        parse_mode=new_message.parse_mode,
        **new_message.media.kwargs,
    )
