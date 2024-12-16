from logging import getLogger
from typing import Optional, Union

from aiogram.types import (
    CallbackQuery,
    Chat,
    ChatJoinRequest,
    ChatMemberUpdated,
    InaccessibleMessage,
    InlineKeyboardButton,
    KeyboardButton,
    Message,
    User,
)

from aiogram_dialog.api.entities import (
    ChatEvent,
    DialogUpdateEvent,
    MediaId,
)
from aiogram_dialog.api.internal import RawKeyboard

logger = getLogger(__name__)

CB_SEP = "\x1D"

REPLY_CALLBACK_SYMBOLS: str = (
    "\u200C"
    "\u200D"
    "\u2060"
    "\u2061"
    "\u2062"
    "\u2063"
    "\u2064"
    "\u00AD"
    "\U0001D173"
    "\U0001D174"
    "\U0001D175"
    "\U0001D176"
    "\U0001D177"
    "\U0001D178"
    "\U0001D179"
    "\U0001D17A"
)


def _encode_reply_callback_byte(byte: int):
    return (
        REPLY_CALLBACK_SYMBOLS[byte % len(REPLY_CALLBACK_SYMBOLS)] +
        REPLY_CALLBACK_SYMBOLS[byte // len(REPLY_CALLBACK_SYMBOLS)]
    )


def encode_reply_callback(data: str) -> str:
    bytes_data = data.encode("utf-8")
    return "".join(
        _encode_reply_callback_byte(byte)
        for byte in bytes_data
    )


def _decode_reply_callback_byte(little: str, big: str) -> int:
    return (
        REPLY_CALLBACK_SYMBOLS.index(big) * len(REPLY_CALLBACK_SYMBOLS) +
        REPLY_CALLBACK_SYMBOLS.index(little)
    )


def join_reply_callback(text: str, callback_data: str) -> str:
    return text + encode_reply_callback(callback_data)


def split_reply_callback(
        data: Optional[str],
) -> tuple[Optional[str], Optional[str]]:
    if not data:
        return None, None
    text = data.rstrip(REPLY_CALLBACK_SYMBOLS)
    callback = data[len(text):]
    return text, decode_reply_callback(callback)


def decode_reply_callback(data: str) -> str:
    bytes_data = bytes(
        _decode_reply_callback_byte(little, big)
        for little, big in zip(data[::2], data[1::2])
    )
    return bytes_data.decode("utf-8")


def _transform_to_reply_button(
        button: Union[InlineKeyboardButton, KeyboardButton],
) -> KeyboardButton:
    if isinstance(button, KeyboardButton):
        return button
    if button.web_app:
        return KeyboardButton(text=button.text, web_app=button.web_app)
    if not button.callback_data:
        raise ValueError(
            "Cannot convert inline button without callback_data or web_app",
        )
    return KeyboardButton(text=join_reply_callback(
        text=button.text, callback_data=button.callback_data,
    ))


def transform_to_reply_keyboard(
        keyboard: list[list[Union[InlineKeyboardButton, KeyboardButton]]],
) -> list[list[KeyboardButton]]:
    return [
        [_transform_to_reply_button(button) for button in row]
        for row in keyboard
    ]


def get_chat(event: ChatEvent) -> Chat:
    if isinstance(
            event,
            (Message, DialogUpdateEvent, ChatMemberUpdated, ChatJoinRequest),
    ):
        return event.chat
    elif isinstance(event, CallbackQuery):
        if not event.message:
            return Chat(id=event.from_user.id, type="")
        return event.message.chat
    else:
        raise TypeError


def is_chat_loaded(chat: Chat) -> bool:
    """
    Check if chat is correctly loaded from telegram.

    For internal events it can be created with no data inside as a FakeChat
    """
    return not getattr(chat, "fake", False)


def is_user_loaded(user: User) -> bool:
    """
    Check if user is correctly loaded from telegram.

    For internal events it can be created with no data inside as a FakeUser
    """
    return not getattr(user, "fake", False)


def get_media_id(
    message: Union[Message, InaccessibleMessage],
) -> Optional[MediaId]:
    if isinstance(message, InaccessibleMessage):
        return None

    media = (
        message.audio or
        message.animation or
        message.document or
        (message.photo[-1] if message.photo else None) or
        message.video or
        message.voice
    )
    if not media:
        return None
    return MediaId(
        file_id=media.file_id,
        file_unique_id=media.file_unique_id,
    )


def intent_callback_data(
        intent_id: str, callback_data: Optional[str],
) -> Optional[str]:
    if callback_data is None:
        return None
    prefix = intent_id + CB_SEP
    if callback_data.startswith(prefix):
        return callback_data
    return prefix + callback_data


def add_intent_id(keyboard: RawKeyboard, intent_id: str):
    for row in keyboard:
        for button in row:
            if isinstance(button, InlineKeyboardButton):
                button.callback_data = intent_callback_data(
                    intent_id, button.callback_data,
                )


def remove_intent_id(callback_data: str) -> tuple[Optional[str], str]:
    if CB_SEP in callback_data:
        intent_id, new_data = callback_data.split(CB_SEP, maxsplit=1)
        return intent_id, new_data
    return None, callback_data
