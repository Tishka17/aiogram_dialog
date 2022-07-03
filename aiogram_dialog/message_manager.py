from logging import getLogger
from typing import IO, Optional, Union

from aiogram import Bot
from aiogram.types import ContentType, InputMedia, Message
from aiogram.utils.exceptions import (
    MessageNotModified, MessageCantBeEdited, MessageToEditNotFound,
    MessageToDeleteNotFound, MessageCantBeDeleted,
)

from .context.events import ShowMode
from .manager.protocols import (
    MediaAttachment, NewMessage, MessageManagerProtocol,
)
from .utils import get_media_id

logger = getLogger(__name__)

SEND_METHODS = {
    ContentType.ANIMATION: "send_animation",
    ContentType.AUDIO: "send_audio",
    ContentType.DOCUMENT: "send_document",
    ContentType.PHOTO: "send_photo",
    ContentType.VIDEO: "send_video",
}


class MessageManager(MessageManagerProtocol):

    async def get_media_source(self, media: MediaAttachment) -> Union[IO, str]:
        if media.file_id:
            return media.file_id.file_id
        if media.url:
            return media.url
        else:
            return open(media.path, "rb")

    async def show_message(self, bot: Bot, new_message: NewMessage,
                           old_message: Optional[Message]):
        if not old_message or new_message.show_mode is ShowMode.SEND:
            logger.debug(
                "Send new message, because: mode=%s, has old_message=%s",
                new_message.show_mode, bool(old_message))
            await self.remove_kbd(bot, old_message)
            return await self.send_message(bot, new_message)

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
                await self.remove_kbd(bot, old_message)
            return await self.send_message(bot, new_message)

        try:
            return await self.edit_message(bot, new_message, old_message)
        except MessageNotModified:
            return old_message
        except (MessageCantBeEdited, MessageToEditNotFound):
            return await self.send_message(bot, new_message)

    async def remove_kbd(self, bot: Bot, old_message: Optional[Message]):
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
    async def edit_message(self, bot: Bot, new_message: NewMessage,
                           old_message: Message):
        if new_message.media:
            if new_message.media.file_id == get_media_id(old_message):
                return await self.edit_caption(bot, new_message, old_message)
            return await self.edit_media(bot, new_message, old_message)
        else:
            return await self.edit_text(bot, new_message, old_message)

    async def edit_caption(self, bot: Bot, new_message: NewMessage,
                           old_message: Message):
        logger.debug("edit_caption to %s", new_message.chat)
        return await bot.edit_message_caption(
            message_id=old_message.message_id,
            chat_id=old_message.chat.id,
            caption=new_message.text,
            reply_markup=new_message.reply_markup,
            parse_mode=new_message.parse_mode,
        )

    async def edit_text(self, bot: Bot, new_message: NewMessage,
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

    async def edit_media(self, bot: Bot, new_message: NewMessage,
                         old_message: Message):
        logger.debug("edit_media to %s, media_id: %s",
                     new_message.chat, new_message.media.file_id)
        media = InputMedia(
            caption=new_message.text,
            reply_markup=new_message.reply_markup,
            parse_mode=new_message.parse_mode,
            disable_web_page_preview=new_message.disable_web_page_preview,
            media=await self.get_media_source(new_message.media),
            type=new_message.media.type,
            **new_message.media.kwargs,
        )
        return await bot.edit_message_media(
            message_id=old_message.message_id,
            chat_id=old_message.chat.id,
            media=media,
            reply_markup=new_message.reply_markup,
        )

    # Send
    async def send_message(self, bot: Bot, new_message: NewMessage):
        if new_message.media:
            return await self.send_media(bot, new_message)
        else:
            return await self.send_text(bot, new_message)

    async def send_text(self, bot: Bot, new_message: NewMessage):
        logger.debug("send_text to %s", new_message.chat)
        return await bot.send_message(
            new_message.chat.id,
            text=new_message.text,
            disable_web_page_preview=new_message.disable_web_page_preview,
            reply_markup=new_message.reply_markup,
            parse_mode=new_message.parse_mode,
        )

    async def send_media(self, bot: Bot, new_message: NewMessage):
        logger.debug("send_media to %s, media_id: %s",
                     new_message.chat, new_message.media.file_id)
        method = getattr(bot, SEND_METHODS[new_message.media.type], None)
        if not method:
            raise ValueError(
                f"ContentType {new_message.media.type} is not supported",
            )
        return await method(
            new_message.chat.id,
            await self.get_media_source(new_message.media),
            caption=new_message.text,
            reply_markup=new_message.reply_markup,
            parse_mode=new_message.parse_mode,
            **new_message.media.kwargs,
        )
