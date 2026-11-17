"""
Example of reply keyboard buttons which ask user for something.

* RequestUsers - choose users
* RequestChat - choose a chat or a channel

The answer comes as a message of a special content type, so it is handled
with MessageInput. Reply buttons cannot be mixed with inline ones in one
window, so every window here has only reply buttons: use /start to go back.
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ContentType, Message

from aiogram_dialog import (
    Dialog,
    DialogManager,
    ShowMode,
    StartMode,
    Window,
    setup_dialogs,
)
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    RequestChat,
    RequestUsers,
)
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.text import Const

API_TOKEN = os.getenv("BOT_TOKEN")


class DialogSG(StatesGroup):
    users = State()
    chat = State()


async def on_users_shared(
    message: Message,
    message_input: MessageInput,
    manager: DialogManager,
):
    users = [user.user_id for user in message.users_shared.users]
    await message.answer(f"You shared users: {users}")
    await manager.switch_to(DialogSG.chat, show_mode=ShowMode.SEND)


async def on_chat_shared(
    message: Message,
    message_input: MessageInput,
    manager: DialogManager,
):
    await message.answer(
        f"You shared chat: {message.chat_shared.chat_id}. "
        f"Click /start to try again",
    )
    await manager.done()


dialog = Dialog(
    Window(
        Const("Choose up to 3 users (not bots):"),
        RequestUsers(
            Const("Share users"),
            request_id=1,
            user_is_bot=False,
            max_quantity=3,
        ),
        MessageInput(
            on_users_shared,
            content_types=[ContentType.USERS_SHARED],
        ),
        markup_factory=ReplyKeyboardFactory(),
        state=DialogSG.users,
    ),
    Window(
        Const("Choose a channel created by you:"),
        RequestChat(
            Const("Share channel"),
            request_id=2,
            chat_is_channel=True,
            chat_is_created=True,
        ),
        MessageInput(on_chat_shared, content_types=[ContentType.CHAT_SHARED]),
        markup_factory=ReplyKeyboardFactory(),
        state=DialogSG.chat,
    ),
)


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.users, mode=StartMode.RESET_STACK)


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    dp.message.register(start, CommandStart())
    dp.include_router(dialog)
    setup_dialogs(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
