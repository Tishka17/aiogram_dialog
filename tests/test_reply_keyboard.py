import pytest
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from aiogram_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
from aiogram_dialog.test_tools import BotClient, MockMessageManager
from aiogram_dialog.test_tools.memory_storage import JsonMemoryStorage
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.text import Const


class MainSG(StatesGroup):
    start = State()


async def on_click(callback: CallbackQuery, _: Button, manager: DialogManager):
    middleware_bot = manager.middleware_data["bot"]
    assert callback.message.bot is middleware_bot

    await manager.done()


dialog = Dialog(
    Window(
        Const("Hello"),
        Button(Const("Button"), id="btn", on_click=on_click),
        state=MainSG.start,
        markup_factory=ReplyKeyboardFactory(),
    ),
)


async def start(_: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


@pytest.mark.asyncio
async def test_reply_keyboard_bot() -> None:
    dp = Dispatcher(storage=JsonMemoryStorage())
    dp.include_router(dialog)
    dp.message.register(start, CommandStart())

    client = BotClient(dp)
    message_manager = MockMessageManager()
    setup_dialogs(dp, message_manager=message_manager)

    await client.send("/start")
    first_message = message_manager.one_message()
    assert first_message.text == "Hello"

    # click button
    reply_keyboard = message_manager.last_reply_markup
    button_text = reply_keyboard.keyboard[0][0].text
    message_manager.reset_history()
    await client.send(button_text)

    assert not message_manager.sent_messages
