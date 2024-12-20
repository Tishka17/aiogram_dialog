from aiogram import F, Router
from aiogram.types import Message

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Checkbox,
    Radio,
    RequestChat,
    RequestContact,
    RequestLocation,
    RequestUser,
    Row,
)
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.text import Const, Format

from . import states
from .common import MAIN_MENU_BUTTON

reply_kbd_router = Router()


@reply_kbd_router.message(F.chat_shared | F.user_shared)
async def on_user_shared(message: Message) -> None:
    if message.chat_shared:
        shifted_id = str(message.chat_shared.chat_id)[4:]
        await message.answer(
            f"ID: <b><code>{message.chat_shared.chat_id}</code></b>\n\n"
            f"Shifted ID: <b><code>{shifted_id}</code></b>",
            parse_mode="HTML",
        )
    elif message.user_shared:
        await message.answer(
            f"User ID: <b><code>{message.user_shared.user_id}</code></b>",
            parse_mode="HTML",
        )


reply_kbd_dialog = Dialog(
    Window(
        Const("Reply keyboard with multiple widgets.\n"),
        Row(
            RequestContact(Const("👤 Send contact")),
            RequestLocation(Const("📍 Send location")),
        ),
        Row(
            RequestChat(
                Const("Request chat"),
                request_id=1,
                chat_is_channel=True,
            ),
            RequestUser(
                Const("Request user"),
                request_id=2,
            ),
            RequestUser(
                Const("Request premium user"),
                request_id=3,
                user_is_premium=True,
            ),
        ),
        Checkbox(
            checked_text=Const("✓ Checkbox"),
            unchecked_text=Const(" Checkbox"),
            id="chk",
        ),
        Radio(
            checked_text=Format("🔘 {item}"),
            unchecked_text=Format("⚪️ {item}"),
            items=["A", "B", "C"],
            item_id_getter=lambda x: x,
            id="radio1",
        ),
        MAIN_MENU_BUTTON,
        markup_factory=ReplyKeyboardFactory(
            input_field_placeholder=Format("{event.from_user.username}"),
            resize_keyboard=True,
        ),
        state=states.ReplyKeyboard.MAIN,
    ),
)
