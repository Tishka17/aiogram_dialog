from logging import getLogger
from typing import Optional, Union

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    ContentType,
    FSInputFile,
    InputFile,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    URLInputFile,
)

from aiogram_dialog.api.entities import MediaAttachment, NewMessage, ShowMode
from aiogram_dialog.api.protocols import (
    MessageManagerProtocol, MessageNotModified,
)
from aiogram_dialog.utils import get_media_id

logger = getLogger(__name__)

SEND_METHODS = {
    ContentType.ANIMATION: "send_animation",
    ContentType.AUDIO: "send_audio",
    ContentType.DOCUMENT: "send_document",
    ContentType.PHOTO: "send_photo",
    ContentType.VIDEO: "send_video",
    ContentType.VIDEO_NOTE: "send_video_note",
    ContentType.DICE: "send_dice",
    ContentType.STICKER: "send_sticker",
    ContentType.VOICE: "send_voice",
}

INPUT_MEDIA_TYPES = {
    ContentType.ANIMATION: InputMediaAnimation,
    ContentType.DOCUMENT: InputMediaDocument,
    ContentType.AUDIO: InputMediaAudio,
    ContentType.PHOTO: InputMediaPhoto,
    ContentType.VIDEO: InputMediaVideo,
}

_INVALID_QUERY_ID_MSG = (
    "query is too old and response timeout expired or query id is invalid"
)


class MessageManager(MessageManagerProtocol):
    async def answer_callback(
            self, bot: Bot, callback_query: CallbackQuery,
    ) -> None:
        try:
            await bot.answer_callback_query(
                callback_query_id=callback_query.id,
            )
        except TelegramAPIError as e:
            if _INVALID_QUERY_ID_MSG in e.message.lower():
                logger.warning("Cannot answer callback: %s", e)
            else:
                raise

    async def get_media_source(
            self, media: MediaAttachment, bot: Bot,
    ) -> Union[InputFile, str]:
        if media.file_id:
            return media.file_id.file_id
        if media.url:
            if media.use_pipe:
                return URLInputFile(media.url, bot=bot)
            return media.url
        else:
            return FSInputFile(media.path)

    def had_media(self, old_message: Message) -> bool:
        return old_message.content_type != ContentType.TEXT

    def need_media(self, new_message: NewMessage) -> bool:
        return bool(new_message.media)

    def _message_changed(
            self, new_message: NewMessage, old_message: Message,
    ) -> bool:
        if new_message.text != old_message.text:
            return True
        if new_message.reply_markup != old_message.reply_markup:
            return True

        if self.had_media(old_message) != self.need_media(new_message):
            return True
        if not self.need_media(new_message):
            return False
        if new_message.media.file_id != get_media_id(old_message):
            return True

        return False

    def _can_edit(self, new_message: NewMessage, old_message: Message) -> bool:
        # we cannot edit message if media appeared or removed
        return self.had_media(old_message) == self.need_media(new_message)

    async def show_message(
            self, bot: Bot, new_message: NewMessage,
            old_message: Optional[Message],
    ) -> Message:
        if not old_message or new_message.show_mode is ShowMode.SEND:
            logger.debug(
                "Send new message, because: mode=%s, has old_message=%s",
                new_message.show_mode,
                bool(old_message),
            )
            await self.remove_kbd(bot, old_message)
            return await self.send_message(bot, new_message)

        if not self._message_changed(new_message, old_message):
            # nothing changed: text, keyboard or media
            return old_message

        if not self._can_edit(new_message, old_message):
            await self.remove_message_safe(bot, old_message)
            return await self.send_message(bot, new_message)

        return await self.edit_message_safe(bot, new_message, old_message)

    # Clear
    async def remove_kbd(
            self, bot: Bot, old_message: Optional[Message],
    ) -> Optional[Message]:
        if not old_message:
            return
        logger.debug("remove_kbd in %s", old_message.chat)
        try:
            return await bot.edit_message_reply_markup(
                message_id=old_message.message_id,
                chat_id=old_message.chat.id,
            )
        except TelegramBadRequest as err:
            if "message is not modified" in err.message:
                pass  # nothing to remove
            elif "message can't be edited" in err.message:
                pass
            elif "message to edit not found" in err.message:
                pass
            else:
                raise err

    async def remove_message_safe(
            self, bot: Bot, old_message: Message,
    ) -> None:
        try:
            await bot.delete_message(
                chat_id=old_message.chat.id,
                message_id=old_message.message_id,
            )
        except TelegramBadRequest as err:
            if (
                    "message to delete not found" in err.message or
                    "message can't be deleted" in err.message
            ):
                await self.remove_kbd(bot, old_message)
            else:
                raise

    # Edit
    async def edit_message_safe(
            self, bot: Bot, new_message: NewMessage, old_message: Message,
    ) -> Message:
        try:
            return await self.edit_message(bot, new_message, old_message)
        except TelegramBadRequest as err:
            if "message is not modified" in err.message:
                raise MessageNotModified from err
            if (
                    "message can't be edited" in err.message or
                    "message to edit not found" in err.message
            ):
                return await self.send_message(bot, new_message)
            else:
                raise

    async def edit_message(
            self, bot: Bot, new_message: NewMessage, old_message: Message,
    ) -> Message:
        if new_message.media:
            if new_message.media.file_id == get_media_id(old_message):
                return await self.edit_caption(bot, new_message, old_message)
            return await self.edit_media(bot, new_message, old_message)
        else:
            return await self.edit_text(bot, new_message, old_message)

    async def edit_caption(
            self, bot: Bot, new_message: NewMessage, old_message: Message,
    ) -> Message:
        logger.debug("edit_caption to %s", new_message.chat)
        return await bot.edit_message_caption(
            message_id=old_message.message_id,
            chat_id=old_message.chat.id,
            caption=new_message.text,
            reply_markup=new_message.reply_markup,
            parse_mode=new_message.parse_mode,
        )

    async def edit_text(
            self, bot: Bot, new_message: NewMessage, old_message: Message,
    ) -> Message:
        logger.debug("edit_text to %s", new_message.chat)
        return await bot.edit_message_text(
            message_id=old_message.message_id,
            chat_id=old_message.chat.id,
            text=new_message.text,
            reply_markup=new_message.reply_markup,
            parse_mode=new_message.parse_mode,
            disable_web_page_preview=new_message.disable_web_page_preview,
        )

    async def edit_media(
            self, bot: Bot, new_message: NewMessage, old_message: Message,
    ) -> Message:
        logger.debug(
            "edit_media to %s, media_id: %s",
            new_message.chat,
            new_message.media.file_id,
        )
        media = INPUT_MEDIA_TYPES[new_message.media.type](
            caption=new_message.text,
            reply_markup=new_message.reply_markup,
            parse_mode=new_message.parse_mode,
            disable_web_page_preview=new_message.disable_web_page_preview,
            media=await self.get_media_source(new_message.media, bot),
            **new_message.media.kwargs,
        )
        return await bot.edit_message_media(
            message_id=old_message.message_id,
            chat_id=old_message.chat.id,
            media=media,
            reply_markup=new_message.reply_markup,
        )

    # Send
    async def send_message(self, bot: Bot, new_message: NewMessage) -> Message:
        if new_message.media:
            return await self.send_media(bot, new_message)
        else:
            return await self.send_text(bot, new_message)

    async def send_text(self, bot: Bot, new_message: NewMessage) -> Message:
        logger.debug("send_text to %s", new_message.chat)
        return await bot.send_message(
            new_message.chat.id,
            text=new_message.text,
            disable_web_page_preview=new_message.disable_web_page_preview,
            reply_markup=new_message.reply_markup,
            parse_mode=new_message.parse_mode,
        )

    async def send_media(self, bot: Bot, new_message: NewMessage) -> Message:
        logger.debug(
            "send_media to %s, media_id: %s",
            new_message.chat,
            new_message.media.file_id,
        )
        method = getattr(bot, SEND_METHODS[new_message.media.type], None)
        if not method:
            raise ValueError(
                f"ContentType {new_message.media.type} is not supported",
            )
        return await method(
            new_message.chat.id,
            await self.get_media_source(new_message.media, bot),
            caption=new_message.text,
            reply_markup=new_message.reply_markup,
            parse_mode=new_message.parse_mode,
            **new_message.media.kwargs,
        )
