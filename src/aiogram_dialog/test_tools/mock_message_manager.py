from copy import deepcopy
from datetime import datetime
from typing import Optional, Set
from uuid import uuid4

from aiogram import Bot
from aiogram.types import (
    Audio, CallbackQuery, Document, Message, PhotoSize, Video,
)

from aiogram_dialog.api.entities import MediaAttachment, NewMessage
from aiogram_dialog.api.protocols import MessageManagerProtocol


def file_id(media: MediaAttachment) -> str:
    return media.file_id or str(uuid4())


MEDIA_CLASSES = {
    "audio": lambda x: Audio(
        file_id=file_id(x), file_unique_id=file_id(x),
        duration=1024,
    ),
    "document": lambda x: Document(
        file_id=file_id(x), file_unique_id=file_id(x),
    ),
    "photo": lambda x: [PhotoSize(
        file_id=file_id(x), file_unique_id=file_id(x),
        width=1024, height=1024,
    )],
    "video": lambda x: Video(
        file_id=file_id(x), file_unique_id=file_id(x),
        width=1024, height=1024, duration=1024,
    ),
}


class MockMessageManager(MessageManagerProtocol):
    def __init__(self):
        self.answered_callbacks: Set[str] = set()
        self.sent_messages = []
        self.last_message_id = 0

    def reset_history(self):
        self.sent_messages.clear()
        self.answered_callbacks.clear()

    def assert_one_message(self) -> None:
        assert len(self.sent_messages) == 1

    def last_message(self) -> Message:
        return self.sent_messages[-1]

    def first_message(self) -> Message:
        return self.sent_messages[0]

    def one_message(self) -> Message:
        self.assert_one_message()
        return self.first_message()

    async def remove_kbd(
            self, bot: Bot, old_message: Optional[Message],
    ) -> Optional[Message]:
        if not old_message:
            return
        data = old_message.model_dump()
        data["reply_markup"] = None
        message = Message(**data)
        self.sent_messages.append(message)
        return message

    async def answer_callback(
            self, bot: Bot, callback_query: CallbackQuery,
    ) -> None:
        self.answered_callbacks.add(callback_query.id)

    def assert_answered(self, callback_id: str) -> None:
        assert callback_id in self.answered_callbacks

    async def show_message(self, bot: Bot, new_message: NewMessage,
                           old_message: Optional[Message]) -> Message:
        message_id = self.last_message_id + 1
        self.last_message_id = message_id

        if new_message.media:
            contents = {
                "caption": new_message.text,
                new_message.media.type: MEDIA_CLASSES[new_message.media.type](
                    new_message.media,
                ),
            }
        else:
            contents = {
                "text": new_message.text,
            }

        message = Message(
            message_id=message_id,
            date=datetime.now(),
            chat=new_message.chat,
            reply_markup=deepcopy(new_message.reply_markup),
            **contents,
        )
        self.sent_messages.append(message)
        return message
