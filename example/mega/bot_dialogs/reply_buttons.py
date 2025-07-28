from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Checkbox,
    Radio,
    RequestChat,
    RequestContact,
    RequestLocation,
    RequestUsers,
    Row,
)
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.text import Const, Format

from . import states
from .common import MAIN_MENU_BUTTON

reply_kbd_dialog = Dialog(
    Window(
        Const("Reply keyboard with multiple widgets.\n"),
        Row(
            RequestContact(Const("👤 Send contact")),
            RequestChat(Const("💬 Send chat"), request_id=1),
            RequestLocation(Const("📍 Send location")),
            RequestUsers(Const("👥 Send user"), request_id=2, max_quantity=1),
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
