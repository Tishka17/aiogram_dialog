import pytest
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from aiogram_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
from aiogram_dialog.test_tools import BotClient, MockMessageManager
from aiogram_dialog.widgets.media.static import StaticMedia


class MainSG(StatesGroup):
    with_url = State()
    with_path = State()


dialog = Dialog(
    Window(
        StaticMedia(url="fake_image.png"),
        state=MainSG.with_url,
    ),
    Window(
        StaticMedia(path="fake_image.png"),
        state=MainSG.with_path,
    ),
)


async def start_url(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.with_url, mode=StartMode.RESET_STACK)


async def start_path(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.with_path, mode=StartMode.RESET_STACK)


@pytest.mark.asyncio
async def test_click():
    dp = Dispatcher(
        storage=MemoryStorage(),
    )
    dp.include_router(dialog)
    dp.message.register(start_url, Command("url"))
    dp.message.register(start_path, Command("path"))

    client = BotClient(dp)
    message_manager = MockMessageManager()
    setup_dialogs(dp, message_manager=message_manager)

    # with url parameter
    await client.send("/url")
    first_message = message_manager.one_message()
    assert first_message.photo

    message_manager.reset_history()

    # with path parameter
    await client.send("/path")
    first_message = message_manager.one_message()
    assert first_message.photo
